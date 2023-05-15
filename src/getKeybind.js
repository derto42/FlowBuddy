const ioHook = require('iohook');

let keysDown = {}; // Object to store keys that are currently being pressed

ioHook.on('keydown', event => {
  keysDown[event.rawcode] = true; // Set the key as being pressed
  handleCombo();
});

ioHook.on('keyup', event => {
  delete keysDown[event.rawcode]; // Remove the key from the pressed keys when it is released
});

function handleCombo() {
  // If there are two keys being pressed simultaneously
  if (Object.keys(keysDown).length === 2) {
    const entry = Object.keys(keysDown).join(',');
    console.log(entry); // Print the key codes to the console
  }
}

ioHook.start();