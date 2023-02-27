import os
from time import sleep
from dotenv import load_dotenv
from slack_bolt import App
from parsers import WeeklyNvimArticleParser

load_dotenv()

BASE_URL = "https://this-week-in-neovim.org"
SLACK_OAUTH_TOKEN = os.environ.get('SLACK_BOT_TOKEN', '')
SLACK_SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET', '')

app = App(
    token = SLACK_OAUTH_TOKEN,
    signing_secret = SLACK_SIGNING_SECRET
)

@app.event('app_mention')
def handle_subscribe(client, event, logger):
    try:
        channel: str = event.get('channel')

        # Create parser and read the latest article
        parser: WeeklyNvimArticleParser = WeeklyNvimArticleParser(BASE_URL)

        # Get the whole document
        texts: list[str] = parser.get_document_text()

        # Divide in pages
        pages = []
        character_count = 0
        current_page = []
        for text_line in texts:
            print(text_line)
            if (character_count + len(text_line) > 2500):
                current_page.append(text_line)
                pages.append(current_page)
                current_page = []
                character_count = 0
                continue
            character_count += len(text_line)
            current_page.append(text_line)
        pages.append(current_page)

        for page in pages:
            # Create block kit to send rich text message
            block_kit = []
            current_block = {}
            current_section = 0
            for text_line in page:
                # Verify this is a heading and the previous block has items, if so, close it and append it.
                if text_line.startswith('*') and text_line.endswith('*') and len(current_block.keys()) > 0:
                    current_section += 1
                    current_block['type'] = 'section'
                    current_block['block_id'] = f"section{current_section}"

                    current_block_text = current_block.get('text', {})
                    current_block_text['type'] = 'mrkdwn'    # type: ignore
                    current_block_text['text'] = current_block_text.get('text', '*')
                    current_block['text'] = current_block_text

                    block_kit.append(current_block)
                    current_block = {}
            
                # Check if text line is that of an image
                if '[IMAGE]' in text_line:
                    # Close the current block
                    current_section += 1
                    current_block['type'] = 'section'
                    current_block['block_id'] = f"section{current_section}"

                    current_block_text = current_block.get('text', {})
                    current_block_text['type'] = 'mrkdwn'    # type: ignore
                    current_block_text['text'] = current_block_text.get('text', '*')
                    current_block['text'] = current_block_text

                    block_kit.append(current_block)
                    current_block = {}

                    # Add an image block below this one
                    url_start = text_line.find('(')
                    url = text_line[url_start+1:-2]
                    image = {}
                    image['type'] = "image"
                    image['image_url'] = url
                    image['alt_text'] = "Image showcasing the plugin"
                    block_kit.append(image)
                else:
                    # Add current line of text
                    current_block_text = current_block.get('text', {})
                    current_block_text['text'] = current_block_text.get('text', '') + text_line + '\n'
                    current_block['text'] = current_block_text

            # Add last non-closed section
            current_section += 1
            current_block['type'] = 'section'
            current_block['block_id'] = f"section{current_section}"
            current_block_text = current_block.get('text', {})
            current_block_text['type'] = 'mrkdwn'    # type: ignore
            current_block_text['text'] = current_block_text.get('text', '*')
            current_block['text'] = current_block_text
            block_kit.append(current_block)

            # Finally send message to chat
            client.chat_postMessage(channel = channel, text="Nvim Weekly News!", blocks = block_kit)
            sleep(3)
    except Exception as e:
        logger.error(f"Error responding to mention: {e}")

if __name__ == '__main__':
    # Start SlackBot
    app.start(port=int(os.environ.get("PORT", 3000)))
 
