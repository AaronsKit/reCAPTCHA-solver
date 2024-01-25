# reCAPTCHA Solver using Selenium and Speech Recognition

This Python script allows you to solve Google reCAPTCHA challenges automatically using Selenium WebDriver and Google Speech Recognition. It's particularly useful for automating tasks that involve reCAPTCHA verification on websites.

## Prerequisites

Before using this script, make sure you have the following dependencies installed:

### Python 3

You can install all the required Python libraries using pip3 by running the following command:

```pip3 install -r requirements.txt```

### ChromeDriver

This script utilizes Selenium WebDriver, which no longer requires you to download ChromeDriver separately. However, to use Selenium with Google Chrome, you will need to have Google Chrome installed on your system.

If you haven't already, you can download and install Google Chrome from the official website: [Google Chrome Download](https://www.google.com/chrome/)

Ensure that you have the latest version of Google Chrome installed for the script to work correctly.

### FFmpeg Dependency

This project relies on FFmpeg for audio file manipulation and conversion. An FFmpeg executable is provided in the `ffmpeg` folder for your convenience.

#### Usage of Provided FFmpeg

The project includes a zipped FFmpeg executable for Mac (ffmpeg.zip) and Windows (ffmpeg.exe.zip) located in the `ffmpeg` folder. Before using the script, you must unzip the appropriate file based on your operating system. It is recommended to use this provided version to ensure compatibility with the script. No additional installation steps are required if you use the provided FFmpeg.

#### Upgrading FFmpeg

If the provided FFmpeg does not work or you wish to upgrade to the latest version, you can download the latest FFmpeg release from the official website:

[Download FFmpeg](https://ffmpeg.org/download.html)

Please download the appropriate version for your operating system. After downloading, replace the old FFmpeg executable in the `ffmpeg` folder with the newly downloaded version. Ensure that the updated FFmpeg executable is named `ffmpeg` or `ffmpeg.exe` and is available in the project's `ffmpeg` folder.

## Usage

1. Clone this repository to your local machine or download the script.
2. Open the script in a text editor or IDE of your choice.
3. Customize the following parameters at the end of the script:
* website_url: The URL of the website with the reCAPTCHA challenge.
* wait: The waiting time in seconds (integer) between actions (adjust as needed). 
* audio_directory: The path to the directory where audio files will be stored.
* ffmpeg: The unzipped ffmpeg file according to your OS. Specify ffmpeg for mac and ffmpeg.exe for Windows.

  Example:

    ```python
    recaptcha_solver(
        "https://www.google.com/recaptcha/api2/demo",
        5,
        "my-path/reCAPTCHA solver/audio",
        "ffmpeg",
    )

4. Run the script using Python 3:

    ```python3 reCAPTCHA_solver.py```

The script will navigate to the specified website, locate and solve the reCAPTCHA challenge, and provide feedback on whether it was successful. It will return None if it could not find the reCAPTCHA, False if it could not solve it and True if reCAPTCHA was solved.

## Important Notes

This script uses Google Speech Recognition for audio challenges. Ensure you have a stable internet connection while running the script.

You may need to customize the code further to fit the specific reCAPTCHA implementation on the website you are targeting.

## Author

AaronsKit

## License

This project is licensed under the MIT License - see the LICENSE file for details.
