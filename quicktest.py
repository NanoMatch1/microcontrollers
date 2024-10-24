from pixis_camera import PIXISCam

class QuickTest:

    def __init__(self):
        self.camera = None

    def process_command(self, command):
        print(f"Processing command: {command}")
        if command == "connect":
            self.connect_to_camera()
        elif command == "disconnect":
            self.disconnect_camera()
        elif command == "acquire":
            self.acquire_image()
        elif command == "exit":
            self.exit_program()
        else:
            print("Invalid command.")

    def connect_to_camera(self):
        self.camera = PIXISCam()
        self.camera.start_ui()  # This remains in the main thread

    def main_loop(self):
        while True:
            command = input("Enter a command: ")
            self.process_command(command)

if __name__ == "__main__":
    qt = QuickTest()
    qt.main_loop()
