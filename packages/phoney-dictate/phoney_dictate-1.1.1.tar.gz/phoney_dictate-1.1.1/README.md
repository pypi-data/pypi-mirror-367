# Phoney Dictate

A voice recognition "app" which sends your cell phone's voice recognition input to your computer.

## Quick start

1. Install from pip

	$ pip install phoney_dictate

2. Run Phoney Dictate on your computer

	$ python3 -m phoney_dictate

3. Generate a bar code - click on the "QR Code" button at the bottom left
corner of the window.

4. Scan the code with your phone and open the link in your browser. (You may
have to use a tool like "Binary Eye")

5. In your phone's browser, place the cursor in the text area. Whatever you
type or dictate there will appear on the Phoney Dictate application.

6. In the Phoney Dictate application, click the "Copy" button to copy the contents
shown there to the clipboard.

7. Paste the text anywhere.

Whatever is displayed in the browser on your phone will be sent to your
computer. After you clear the text, and enter new text, only the new text will
be copied over. The old text will be gone.

Ctrl-Q exits the Phoney Dictate application on your computer. The browser component
is just a webpage, so you would close it like you normally would any webpage.

## Troubleshooting

Both your phone and your computer need to be on the same local network. Usually
this is the case if your phone and computer are connected to the same router.

This should also work if your computer is set up as a hot spot, although it
hasn't been tested.

If you have a firewall installed on your computer, (such as UFW), make sure
that port 8585 is open for listening.

