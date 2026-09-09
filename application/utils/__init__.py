from pyfiglet import Figlet


def banner():
    f = Figlet(font="dos_rebel")
    ascii_art = f.renderText("NBC")

    width = 80
    line = "=" * width

    print("\n" + line)
    print("Welcome to NBC :: System Integration Service\n")
    print(ascii_art.rstrip())
    print("Made with Love, Ponloeng Bora")
    print(":: https://www.nbc.gov.kh/ ::")
    print(line + "\n")


if __name__ == "__main__":
    banner()
