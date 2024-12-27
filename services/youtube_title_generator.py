import anthropic
import os
from dotenv import load_dotenv
import cv2
from shared.models import SocialMediaPost
from shared.utils import image_to_base64
import shutil

load_dotenv()


def make_request_claude(frames_dir: str, original_comment: str) -> str:
    prompt = "Here are some random frames from a video. Your job is to analyse these and create an appropriate title for the video which will be uploaded to youtube. Try to make the title interesting, unique and fairly short - max. 3-4 words. Also, avoid cliches.\n\nOutput ONLY the title, with no additional explanation or text."

    if len(original_comment) > 0:
        prompt = f"Here are some random frames from a video and a description. Your job is to analyse these and create an appropriate title for the video which will be uploaded to youtube. This is from a community so try not to reference things from the comment that might only be relevant to people in the community. Try to make the title interesting, unique and fairly short - max. 3-4 words. Also, avoid cliches.\n\nArtist's comment: \"{original_comment}\"\n\nIf they have included what looks like a title in the comment, please use this.\n\nOutput ONLY the title, with no additional explanation or text."

    image_paths = [os.path.join(frames_dir, x) for x in os.listdir(frames_dir)]
    content = []

    for image_path in image_paths:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": image_to_base64(image_path)
            }
        })
    content.append(
        {
            "type": "text",
            "text": "\n" + prompt
        }
    )

    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": content
            }
        ]
    )
    return message.content[0].text


def extract_evenly_distributed_frames(video_path, num_frames, img_prefix, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    vidcap = cv2.VideoCapture(video_path)

    # Get the total number of frames
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calculate the interval between frames
    frames_interval = total_frames // num_frames

    frame_count = 0
    success = True

    while success and frame_count < num_frames:
        # Set the video capture to the current frame position
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_count * frames_interval)

        success, image = vidcap.read()

        if success:
            save_path = os.path.join(
                save_dir, f"{img_prefix}_{frame_count}.jpg")
            cv2.imwrite(save_path, image)

            frame_count += 1
        else:
            break

    vidcap.release()


def create_youtube_title_using_claude(post_id: int, file_local_path: str, original_comment: str) -> str:
    frames_dir = os.path.join("temp", str(post_id))

    # claude can use 20 images max
    extract_evenly_distributed_frames(
        video_path=file_local_path, num_frames=3, img_prefix=post_id, save_dir=frames_dir)

    video_title = make_request_claude(
        frames_dir=frames_dir, original_comment=original_comment)

    # delete folder with frames
    shutil.rmtree(frames_dir)

    return video_title
