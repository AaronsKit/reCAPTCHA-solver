import subprocess
import time
import os
import re
import requests
import sys

import speech_recognition as sr
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


# Function to determine the ffmpeg resource path
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# Function to locate the reCAPTCHA frames
def frame(driver, wait):
    # Add wait time for all elements to become available
    time.sleep(wait)

    frames = driver.find_elements(By.TAG_NAME, "iframe")

    recaptcha_control_frame = None
    recaptcha_challenge_frame = None

    for frame in frames:
        # Find the reCAPTCHA checkbox
        if re.search("reCAPTCHA", frame.get_attribute("title")):
            recaptcha_control_frame = frame
            print("[INF] ReCAPTCHA box located")

        # Find the reCAPTCHA visual/audio puzzle
        if re.search(
            "recaptcha challenge expires in two minutes", frame.get_attribute("title")
        ):
            recaptcha_challenge_frame = frame
            print("[INF] ReCAPTCHA puzzle located")

    return recaptcha_control_frame, recaptcha_challenge_frame


# Function to check if reCAPTCHA is solved
def check_solved(driver, wait):
    try:
        WebDriverWait(driver, wait).until(
            expected_conditions.element_to_be_clickable(
                (
                    By.XPATH,
                    r".//li/input[@id='recaptcha-demo-submit']",
                )
            )
        )

        print("[INF] ReCAPTCHA successfully solved")
        solved = True

    except:
        solved = False

    return solved


# Function to solve reCAPTCHA
def recaptcha_solver(website_url, wait, audio_directory, ffmpeg):
    # Create a new instance of the Chrome browser
    driver = webdriver.Chrome(service=Service())

    # Navigate to the website
    driver.get(website_url)

    recaptcha_count = 0
    success = None
    is_recaptcha_control_active = True

    print("\n[INF] Trying to find reCAPTCHA")

    recaptcha_control_frame, recaptcha_challenge_frame = frame(driver, wait)

    # Find reCAPTCHA
    if not (recaptcha_control_frame and recaptcha_challenge_frame):
        print("[ERR] Unable to find reCAPTCHA")
        is_recaptcha_control_active = False

    while is_recaptcha_control_active:
        recaptcha_count += 1

        # Make sure that reCAPTCHA does not get stuck in a loop
        if recaptcha_count >= 3:
            print("[ERR] IP address has been blocked by reCAPTCHA or network error")
            success = False
            break  # end, not solved

        try:
            # Switch to checkbox
            driver.switch_to.default_content()
            driver.switch_to.frame(recaptcha_control_frame)

            # Click on checkbox to activate reCAPTCHA
            WebDriverWait(driver, wait).until(
                expected_conditions.element_to_be_clickable(
                    (By.CLASS_NAME, "recaptcha-checkbox-border")
                )
            ).click()

            print("[INF] Checkbox clicked")

        except:
            print("[ERR] Cannot solve reCAPTCHA checkbox")
            success = False
            break  # end, not solved

        if check_solved(driver, wait):
            success = True
            break  # end, solved
        else:
            is_recaptcha_challenge_active = True
            switched_to_audio = False

            while is_recaptcha_challenge_active:
                if not switched_to_audio:
                    # Click on voice challenge button
                    try:
                        driver.switch_to.default_content()
                        driver.switch_to.frame(recaptcha_challenge_frame)

                        WebDriverWait(driver, wait).until(
                            expected_conditions.element_to_be_clickable(
                                (By.ID, "recaptcha-audio-button")
                            )
                        ).click()

                        print("[INF] Switched to audio control frame")
                        switched_to_audio = True

                    except:
                        print("[INF] Recurring checkbox")
                        break  # return to checkbox

                # Get the audio source (the mp3 file)
                try:
                    # Switch to reCAPTCHA audio challenge frame
                    driver.switch_to.default_content()
                    driver.switch_to.frame(recaptcha_challenge_frame)

                    # Get the mp3 audio file
                    time.sleep(wait)
                    src = driver.find_element(By.ID, "audio-source").get_attribute(
                        "src"
                    )

                except Exception as e:
                    print("[ERR] Error when using Audio challenge frame")
                    print(e)
                    success = False
                    is_recaptcha_control_active = False
                    break  # end, not solved

                file_path_mp3 = os.path.normpath(
                    os.path.join(audio_directory, "sample.mp3")
                )
                file_path_wav = os.path.normpath(
                    os.path.join(audio_directory, "sample.wav")
                )

                try:
                    s = requests.Session()

                    local_filename = "sample.mp3"
                    r = s.get(src, verify=False)
                    with open(os.path.join(audio_directory, local_filename), "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)

                except Exception as e:
                    print("[ERR] Could not download audio file")
                    print(e)
                    success = False
                    is_recaptcha_control_active = False
                    break  # end, not solved

                # Mp3 to wav conversion using ffmpeg
                try:
                    ffmpeg_path = os.path.join(
                        "." + os.sep + "ffmpeg" + os.sep + ffmpeg
                    )
                    commands_list = [
                        resource_path(ffmpeg_path),
                        "-i",
                        file_path_mp3,
                        "-y",
                        file_path_wav,
                    ]

                    if subprocess.run(commands_list).returncode == 0:
                        print("[INF] Exported audio file to .wav")
                    else:
                        raise

                except Exception as e:
                    print(
                        "[ERR] Could not run ffmpeg script. Ensure that the latest version of ffmpeg is downloaded and is in the correct folder. Visit https://ffmpeg.org/download.html#build-mac to download the latest file."
                    )
                    print(e)
                    success = False
                    is_recaptcha_control_active = False
                    break  # end, not solved

                # Translate audio to text with Google voice recognition
                time.sleep(wait)
                r = sr.Recognizer()
                sample_audio = sr.AudioFile(file_path_wav)
                time.sleep(wait)

                with sample_audio as source:
                    audio = r.record(source)
                    try:
                        key = r.recognize_google(audio)
                        print(f"[INF] ReCAPTCHA Passcode: {key}")
                        print("[INF] Audio Snippet was recognized")
                    except Exception as e:
                        print(
                            "[ERR] ReCAPTCHA voice segment is too difficult to solve."
                        )
                        print(e)
                        success = False
                        is_recaptcha_control_active = False
                        break  # end, not solved

                    # Key in results and submit
                    time.sleep(wait)
                    try:
                        driver.find_element(By.ID, "audio-response").send_keys(
                            key.lower()
                        )
                        driver.find_element(By.ID, "audio-response").send_keys(
                            Keys.ENTER
                        )
                        time.sleep(wait)
                        driver.switch_to.default_content()
                        print("[INF] Audio snippet submitted")
                    except Exception as e:
                        print("[ERR] IP address might have been blocked for reCAPTCHA")
                        print(e)
                        success = False
                        is_recaptcha_control_active = False
                        break  # end, not solved

                    # Check if reCAPTCHA has been solved
                    if check_solved(driver, wait):
                        success = True
                        is_recaptcha_control_active = False
                        break  # end, solved

    return success


recaptcha_solver(
    "https://www.google.com/recaptcha/api2/demo",
    "[add integer wait time here]",
    "[add path to audio folder here]",
    "[Specify ffmpeg executable (ffmpeg for mac or ffmpeg.exe for windows)]",
)
