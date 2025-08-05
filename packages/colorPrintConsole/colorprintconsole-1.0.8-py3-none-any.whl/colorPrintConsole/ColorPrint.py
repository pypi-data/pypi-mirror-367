class ColorPrint:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

    @staticmethod
    def _print_color(code: str, *args):
        print(code + " ".join(map(str, args)) + ColorPrint.RESET)

    @staticmethod
    def red(*args):
        ColorPrint._print_color(ColorPrint.RED, *args)

    @staticmethod
    def green(*args):
        ColorPrint._print_color(ColorPrint.GREEN, *args)

    @staticmethod
    def yellow(*args):
        ColorPrint._print_color(ColorPrint.YELLOW, *args)

    @staticmethod
    def blue(*args):
        ColorPrint._print_color(ColorPrint.BLUE, *args)

    @staticmethod
    def magenta(*args):
        ColorPrint._print_color(ColorPrint.MAGENTA, *args)

    @staticmethod
    def cyan(*args):
        ColorPrint._print_color(ColorPrint.CYAN, *args)

    @staticmethod
    def color_hex(color_hex: str, *args):
        # 去除可能的 '#'
        color_hex = color_hex.lstrip("#")
        # 将 hex 转换为 RGB
        r, g, b = (
            int(color_hex[0:2], 16),
            int(color_hex[2:4], 16),
            int(color_hex[4:6], 16),
        )
        # 构建 ANSI 转义序列并打印
        print(f'\033[38;2;{r};{g};{b}m{" ".join(map(str, args))}\033[0m')


if __name__ == "__main__":
    ColorPrint.red("This is red.")
    ColorPrint.green("This is green.")
    ColorPrint.yellow("This is yellow.")
    ColorPrint.blue("This is blue.")
    ColorPrint.magenta("This is magenta.")
    ColorPrint.cyan("This is cyan.")
    ColorPrint.color_hex("FFC0CB", "This is pink.")
    ColorPrint.color_hex("#800080", "This is purple.")
