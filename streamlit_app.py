import streamlit as st
import ffmpeg
import os
import tempfile
import zipfile

def process_video(input_path, output_path, preset):
    try:
        # Strip metadata
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(stream, output_path, map_metadata=-1)
        ffmpeg.run(stream, overwrite_output=True)

        # Apply preset transformations
        if preset == 1:
            # Preset 1: Slight Crop & Saturation
            stream = ffmpeg.input(output_path)
            stream = ffmpeg.filter(stream, 'crop', '100%:90%')
            stream = ffmpeg.filter(stream, 'eq', saturation=1.1)
            stream = ffmpeg.output(stream, f"{output_path}_temp")
            ffmpeg.run(stream, overwrite_output=True)
            os.replace(f"{output_path}_temp", output_path)
        elif preset == 2:
            # Preset 2: Resize & Brightness Adjustment
            stream = ffmpeg.input(output_path)
            stream = ffmpeg.filter(stream, 'scale', '0.95*iw', '0.95*ih')
            stream = ffmpeg.filter(stream, 'eq', brightness=0.07)
            stream = ffmpeg.output(stream, f"{output_path}_temp")
            ffmpeg.run(stream, overwrite_output=True)
            os.replace(f"{output_path}_temp", output_path)
        elif preset == 3:
            # Preset 3: Time Shift
            stream = ffmpeg.input(output_path)
            stream = ffmpeg.filter(stream, 'setpts', '0.97*PTS')
            stream = ffmpeg.output(stream, f"{output_path}_temp")
            ffmpeg.run(stream, overwrite_output=True)
            os.replace(f"{output_path}_temp", output_path)

        # Increase saturation by 10%
        stream = ffmpeg.input(output_path)
        stream = ffmpeg.filter(stream, 'eq', saturation=1.1)
        stream = ffmpeg.output(stream, f"{output_path}_temp")
        ffmpeg.run(stream, overwrite_output=True)
        os.replace(f"{output_path}_temp", output_path)

        # Change MD5 hash
        with open(output_path, 'ab') as f:
            f.write(os.urandom(10))

    except ffmpeg.Error as e:
        st.error(f"An error occurred while processing the video: {e.stderr.decode()}")
        return False
    return True

def main():
    st.title("Video Variation Tool")
    st.write("Upload a video to create 3 variations with different presets.")

    uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov"])

    if uploaded_file is not None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, "input_video")
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            output_paths = []
            for i in range(1, 4):
                output_path = os.path.join(temp_dir, f"output_video_{i}.mp4")
                if process_video(input_path, output_path, i):
                    output_paths.append(output_path)

            if len(output_paths) == 3:
                zip_path = os.path.join(temp_dir, "video_variations.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for path in output_paths:
                        zipf.write(path, os.path.basename(path))

                with open(zip_path, "rb") as f:
                    st.download_button(
                        label="Download Video Variations",
                        data=f,
                        file_name="video_variations.zip",
                        mime="application/zip"
                    )
            else:
                st.error("An error occurred while processing the video. Please try again.")

if __name__ == "__main__":
    main()