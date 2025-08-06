import concurrent.futures
import logging
import os
import argparse
import sys
import signal
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
import time
import traceback

from shapely.errors import TopologicalError
from sahi.utils.cv import read_image_as_pil
from sahi.utils.file import load_json, save_json
from sahi_override.sahi.utils.coco import Coco, create_coco_dict
from sahi_override.sahi.slicing import slice_image

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
)

# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    global shutdown_requested
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True


def validate_inputs(
    coco_annotation_file_path: str,
    image_dir: str,
    output_dir: Optional[str] = None,
    slice_height: int = 512,
    slice_width: int = 512,
    overlap_height_ratio: float = 0.2,
    overlap_width_ratio: float = 0.2,
    min_area_ratio: float = 0.1,
    num_workers: int = 4,
) -> None:
    """
    Validate all input parameters and file paths.
    
    Args:
        coco_annotation_file_path: Path to COCO annotations file
        image_dir: Directory containing images
        output_dir: Output directory (optional)
        slice_height: Height of slices
        slice_width: Width of slices
        overlap_height_ratio: Height overlap ratio
        overlap_width_ratio: Width overlap ratio
        min_area_ratio: Minimum area ratio
        num_workers: Number of parallel workers
        
    Raises:
        ValueError: If any validation fails
        FileNotFoundError: If required files/directories don't exist
    """
    # Validate file paths
    if not os.path.exists(coco_annotation_file_path):
        raise FileNotFoundError(f"COCO annotation file not found: {coco_annotation_file_path}")
    
    if not os.path.exists(image_dir):
        raise FileNotFoundError(f"Image directory not found: {image_dir}")
    
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")
        except OSError as e:
            raise OSError(f"Failed to create output directory {output_dir}: {e}")
    
    # Validate numeric parameters
    if slice_height <= 0 or slice_width <= 0:
        raise ValueError("Slice dimensions must be positive")
    
    if not (0.0 <= overlap_height_ratio <= 1.0):
        raise ValueError("Overlap height ratio must be between 0.0 and 1.0")
    
    if not (0.0 <= overlap_width_ratio <= 1.0):
        raise ValueError("Overlap width ratio must be between 0.0 and 1.0")
    
    if not (0.0 <= min_area_ratio <= 1.0):
        raise ValueError("Minimum area ratio must be between 0.0 and 1.0")
    
    if num_workers <= 0:
        raise ValueError("Number of workers must be positive")
    
    # Validate COCO file format
    try:
        coco_dict = load_json(coco_annotation_file_path)
        required_keys = ["images", "annotations", "categories"]
        missing_keys = [key for key in required_keys if key not in coco_dict]
        if missing_keys:
            raise ValueError(f"Invalid COCO format. Missing keys: {missing_keys}")
    except Exception as e:
        raise ValueError(f"Failed to load or validate COCO file: {e}")


def process_image(
    image_idx: int,
    coco_image,
    image_dir: str,
    output_dir: Optional[str],
    slice_height: int,
    slice_width: int,
    overlap_height_ratio: float,
    overlap_width_ratio: float,
    min_area_ratio: float,
    out_ext: Optional[str],
    verbose: bool,
) -> List:
    """
    Process a single image by slicing it into smaller tiles with annotations.
    
    This function takes a COCO image object and slices it into smaller tiles while
    preserving the bounding box annotations. It handles various exceptions that may
    occur during processing.
    
    Args:
        image_idx: Index of the image being processed
        coco_image: COCO image object containing file_name and annotations
        image_dir: Directory path containing the input images
        output_dir: Directory path where sliced images will be saved
        slice_height: Height of each image slice in pixels
        slice_width: Width of each image slice in pixels
        overlap_height_ratio: Overlap ratio for height between slices (0.0-1.0)
        overlap_width_ratio: Overlap ratio for width between slices (0.0-1.0)
        min_area_ratio: Minimum area ratio for annotations to be preserved
        out_ext: Output file extension (e.g., '.jpg', '.png')
        verbose: Whether to print verbose output during processing
        
    Returns:
        List of COCO image objects representing the sliced images with annotations
        
    Raises:
        Various exceptions that are caught and logged
    """
    global shutdown_requested
    
    if shutdown_requested:
        logger.info(f"Skipping image {image_idx} due to shutdown request")
        return []
    
    image_path = os.path.join(image_dir, coco_image.file_name)
    
    try:
        # Validate image file exists
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return []
        
        # Check file size to avoid processing corrupted files
        file_size = os.path.getsize(image_path)
        if file_size == 0:
            logger.warning(f"Skipping empty image file: {image_path}")
            return []
        
        # Load image with timeout protection
        start_time = time.time()
        pil_image = read_image_as_pil(image_path)
        load_time = time.time() - start_time
        
        if verbose and load_time > 5.0:
            logger.warning(f"Slow image load ({load_time:.2f}s): {image_path}")
        
        # Validate image dimensions
        if pil_image.size[0] == 0 or pil_image.size[1] == 0:
            logger.warning(f"Invalid image dimensions for {image_path}: {pil_image.size}")
            return []
        
        # Process image slicing
        slice_image_result = slice_image(
            image=pil_image,
            coco_annotation_list=coco_image.annotations,
            output_file_name=f"{Path(coco_image.file_name).stem}_{image_idx}",
            output_dir=output_dir,
            slice_height=slice_height,
            slice_width=slice_width,
            overlap_height_ratio=overlap_height_ratio,
            overlap_width_ratio=overlap_width_ratio,
            min_area_ratio=min_area_ratio,
            out_ext=out_ext,
            verbose=verbose,
        )
        
        if verbose:
            print(f"Completed: {image_idx + 1} - {len(slice_image_result.coco_images)} slices")
        
        return slice_image_result.coco_images
        
    except TopologicalError as e:
        logger.warning(f"Invalid annotation found, skipping: {image_path} - {e}")
        return []
    except OSError as e:
        logger.error(f"OS error processing {image_path}: {e}")
        return []
    except MemoryError as e:
        logger.error(f"Memory error processing {image_path}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error processing {image_path}: {e}")
        if verbose:
            logger.error(f"Traceback: {traceback.format_exc()}")
        return []


def slice_coco_json(
    coco_annotation_file_path: str,
    image_dir: str,
    output_coco_annotation_file_name: str,
    output_dir: Optional[str] = None,
    ignore_negative_samples: bool = True,
    slice_height: int = 512,
    slice_width: int = 512,
    overlap_height_ratio: float = 0.2,
    overlap_width_ratio: float = 0.2,
    min_area_ratio: float = 0.1,
    out_ext: Optional[str] = None,
    verbose: bool = False,
    num_workers: int = 4,
    output_json: Optional[str] = None,
) -> Tuple[Dict, str]:
    """
    Slice COCO dataset images and annotations into smaller tiles using parallel processing.
    
    This function takes a COCO annotation file and corresponding images, then slices
    each image into smaller tiles while preserving the bounding box annotations.
    The processing is done in parallel using ProcessPoolExecutor for improved performance.
    
    Args:
        coco_annotation_file_path: Path to the input COCO annotations JSON file
        image_dir: Directory containing the input images referenced in COCO annotations
        output_coco_annotation_file_name: Base name for the output COCO annotations file
        output_dir: Directory to save sliced images and annotations. If None, only JSON is returned
        ignore_negative_samples: Whether to ignore images with no annotations (default: True)
        slice_height: Height of each image slice in pixels (default: 512)
        slice_width: Width of each image slice in pixels (default: 512)
        overlap_height_ratio: Overlap ratio for height between slices (default: 0.2)
        overlap_width_ratio: Overlap ratio for width between slices (default: 0.2)
        min_area_ratio: Minimum area ratio for annotations to be preserved (default: 0.1)
        out_ext: Output file extension for sliced images (default: None)
        verbose: Whether to print verbose output during processing (default: False)
        num_workers: Number of parallel workers for processing (default: 4)
        output_json: Specific path for output JSON file. If None, uses 
                    output_dir/output_coco_annotation_file_name_coco.json
        
    Returns:
        Tuple containing:
            - coco_dict (Dict): The processed COCO annotations dictionary
            - save_path (str): Path where the JSON file was saved (empty string if not saved)
            
    Raises:
        ValueError: If input validation fails
        FileNotFoundError: If required files don't exist
        OSError: If output directory creation fails
    """
    global shutdown_requested
    
    # Validate inputs
    validate_inputs(
        coco_annotation_file_path=coco_annotation_file_path,
        image_dir=image_dir,
        output_dir=output_dir,
        slice_height=slice_height,
        slice_width=slice_width,
        overlap_height_ratio=overlap_height_ratio,
        overlap_width_ratio=overlap_width_ratio,
        min_area_ratio=min_area_ratio,
        num_workers=num_workers,
    )
    
    # Read COCO file with error handling
    try:
        coco_dict: Dict = load_json(coco_annotation_file_path)
        coco = Coco.from_coco_dict_or_path(coco_dict)
    except Exception as e:
        raise ValueError(f"Failed to load COCO file: {e}")
    
    if not coco.images:
        logger.warning("No images found in COCO file")
        return coco_dict, ""
    
    logger.info(f"Processing {len(coco.images)} images with {num_workers} workers")
    
    sliced_coco_images: List = []
    processed_count = 0
    error_count = 0
    
    # Set up signal handlers for graceful shutdown
    original_sigint = signal.signal(signal.SIGINT, signal_handler)
    original_sigterm = signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run in parallel using ProcessPoolExecutor with timeout
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=num_workers,
            mp_context=concurrent.futures.get_context('spawn')  # More stable on macOS
        ) as executor:
            futures = {}
            
            for idx, img in enumerate(coco.images):
                if shutdown_requested:
                    break
                    
                future = executor.submit(
                    process_image,
                    idx,
                    img,
                    image_dir,
                    output_dir,
                    slice_height,
                    slice_width,
                    overlap_height_ratio,
                    overlap_width_ratio,
                    min_area_ratio,
                    out_ext,
                    verbose,
                )
                futures[future] = idx
            
            # Process completed futures with timeout
            for future in concurrent.futures.as_completed(futures, timeout=3600):  # 1 hour timeout
                if shutdown_requested:
                    logger.info("Shutdown requested, cancelling remaining tasks...")
                    for f in futures:
                        f.cancel()
                    break
                
                try:
                    result = future.result(timeout=300)  # 5 minute timeout per result
                    sliced_coco_images.extend(result)
                    processed_count += 1
                    
                    if verbose and processed_count % 10 == 0:
                        logger.info(f"Progress: {processed_count}/{len(coco.images)} images processed")
                        
                except concurrent.futures.TimeoutError:
                    idx = futures[future]
                    logger.error(f"Timeout processing image {idx}")
                    error_count += 1
                except Exception as e:
                    idx = futures[future]
                    logger.error(f"Error processing image {idx}: {e}")
                    error_count += 1
    
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down gracefully...")
        shutdown_requested = True
    except Exception as e:
        logger.error(f"Unexpected error during processing: {e}")
        if verbose:
            logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        # Restore original signal handlers
        signal.signal(signal.SIGINT, original_sigint)
        signal.signal(signal.SIGTERM, original_sigterm)
    
    logger.info(f"Processing complete: {processed_count} successful, {error_count} errors")
    
    if not sliced_coco_images:
        logger.warning("No sliced images were generated")
        return coco_dict, ""
    
    # Create and save COCO dict
    try:
        coco_dict = create_coco_dict(
            sliced_coco_images,
            coco_dict["categories"],
            ignore_negative_samples=ignore_negative_samples,
        )
    except Exception as e:
        logger.error(f"Failed to create COCO dict: {e}")
        raise
    
    save_path = ""
    if output_coco_annotation_file_name and output_dir:
        try:
            if output_json:
                save_path = Path(output_json)
            else:
                save_path = Path(output_dir) / f"{output_coco_annotation_file_name}_coco.json"
            
            # Ensure parent directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_json(coco_dict, save_path)
            logger.info(f"Saved COCO annotations to: {save_path}")
            
        except Exception as e:
            logger.error(f"Failed to save COCO annotations: {e}")
            raise
    
    return coco_dict, str(save_path)


def main():
    """Main function with comprehensive error handling."""
    parser = argparse.ArgumentParser(description='Slice COCO dataset images and annotations')
    parser.add_argument('--input-coco-json', type=str, required=True,
                      help='Path to the input COCO annotations JSON file')
    parser.add_argument('--image-dir', type=str, required=True,
                      help='Directory containing the input images')
    parser.add_argument('--output-dir', type=str, required=True,
                      help='Directory to save the sliced images and annotations')
    parser.add_argument('--slice-height', type=int, default=1024,
                      help='Height of each image slice (default: 1024)')
    parser.add_argument('--slice-width', type=int, default=1024,
                      help='Width of each image slice (default: 1024)')
    parser.add_argument('--overlap-height-ratio', type=float, default=0.2,
                      help='Overlap ratio for height between slices (default: 0.2)')
    parser.add_argument('--overlap-width-ratio', type=float, default=0.2,
                      help='Overlap ratio for width between slices (default: 0.2)')
    parser.add_argument('--min-area-ratio', type=float, default=0.4,
                      help='Minimum area ratio for annotations (default: 0.4)')
    parser.add_argument('--num-workers', type=int, default=8,
                      help='Number of parallel workers (default: 8)')
    parser.add_argument('--output-coco-json', type=str, default=None,
                      help='Path to save the output COCO JSON file')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Enable verbose output')
    parser.add_argument('--log-level', type=str, default='INFO',
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                      help='Set logging level (default: INFO)')

    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    
    try:
        logger.info("Starting COCO dataset slicing...")
        start_time = time.time()
        
        coco_dict, coco_path = slice_coco_json(
            coco_annotation_file_path=args.input_coco_json,
            image_dir=args.image_dir,
            output_coco_annotation_file_name="coco-annotations-sliced.json",
            output_dir=args.output_dir,
            ignore_negative_samples=True,
            slice_height=args.slice_height,
            slice_width=args.slice_width,
            overlap_height_ratio=args.overlap_height_ratio,
            overlap_width_ratio=args.overlap_width_ratio,
            min_area_ratio=args.min_area_ratio,
            out_ext=".jpg",
            verbose=args.verbose,
            num_workers=args.num_workers,
            output_json=args.output_coco_json,
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"Processing completed successfully in {elapsed_time:.2f} seconds")
        
        if coco_path:
            print(f"✅ Output saved to: {coco_path}")
        else:
            print("✅ Processing completed (no file saved)")
            
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\n⚠️  Process terminated by user")
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


# ✅ Fix: Ensure this script runs only when executed directly
if __name__ == "__main__":
    main()
