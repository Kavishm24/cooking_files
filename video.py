import subprocess
import os

def read_links(file_path):
    """Reads links from a given file."""
    with open(file_path, 'r') as file:
        links = file.readlines()
    return [link.strip() for link in links if link.strip()]

def run_command(link, download_folder):
    """Runs the command 'yt-dlp <link>' and returns the output."""
    # Ensure the download folder exists
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    # Set the output template for yt-dlp
    output_template = os.path.join(download_folder, '%(title)s.%(ext)s')
    
    command = f'yt-dlp -f "bestvideo[height<=1080][vcodec!=av01]+bestaudio[acodec!=opus]" --merge-output-format mp4 -o "{output_template}" "{link}"'
    try:
        # Execute the command and capture the output
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)

def log_results(link, output, error, log_file):
    """Logs the output and error of the command to a log file."""
    with open(log_file, 'a') as log:
        log.write(f"Link: {link}\n")
        log.write(f"Output: {output}\n")
        if error:
            log.write(f"Error: {error}\n")
        log.write("\n")

def main():
    input_file = 'links.txt'  # The file with links
    log_file = 'download_log.txt'  # The file to log results
    download_folder = 'downloads'  # The folder to save the files

    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"The file {input_file} does not exist.")
        return

    # Clear the log file if it exists
    open(log_file, 'w').close()

    links = read_links(input_file)
    for link in links:
        output, error = run_command(link, download_folder)
        log_results(link, output, error, log_file)

if __name__ == "__main__":
    main()
