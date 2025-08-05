import os
import math
import sys
import time
import click
import re
import curses
from typing import List, Optional, Tuple, Union
from art import text2art
from rich.console import Console, Group
from rich.table import Table
from rich.progress import Progress, track
from rich.live import Live
from rich.panel import Panel
from rich.measure import Measurement
from rich.align import Align
from rich.text import Text
from pyfiglet import CharNotPrinted, Figlet

FONT = 'univers'
console = Console()

##########################
#  ASCII TEXT GENERATOR  #
# USED FOR DRAW FUNCTION #
##########################

def asciiTextGenerator(
    text: str,
    font: str = "c1",
    color: str = "cyan",
    use_text2art: bool = True
):
   
    if use_text2art == True:
        asciiText = text2art(text, font=font)
    else:
        figlet = Figlet(font=font)
        asciiText = figlet.renderText(text)
       
    renderedText = Text(asciiText, style=color)
    FinalText = Align.center(renderedText, vertical="middle", height=console.height)
   
    return FinalText

#################
# DRAW FUNCTION #
#################

def draw(
    text: str,
    optional_small_text: Optional[str] = None,
    font: str = "c1",
    color: str = "cyan",
    use_panel: bool = False,
    use_text2art: bool = True,
    sleep_time: float = 1.0,
    live_context=None
) -> None:
    FinalText = asciiTextGenerator(text, font, color, use_text2art)
   
    if use_panel == False:
        try:
            if live_context:
                live_context.update(FinalText) #asked ai how to stop flickering and it gave me this
                time.sleep(sleep_time)
            else:
                with Live(FinalText, refresh_per_second=4, screen=True) as live:
                    time.sleep(sleep_time)
        except Exception as e:
            print(f"Error: {e}")
            print("kod yarrağı yemiş durumda -ruhlar aleminden ferruh")
    else:
        print("sonra")

def stopwatch():
    start_time = time.time()
    try:
        with Live(screen=True, refresh_per_second=4) as live:
            while True:
                elapsed = int(time.time() - start_time)
                minutes = elapsed // 60
                seconds = elapsed % 60
                time_str = f"{minutes:02}:{seconds:02}"
                
                draw(
                    text=time_str,
                    color="cyan",
                    sleep_time=0.25,
                    live_context=live
                )
           
    except KeyboardInterrupt:
        console.clear()
        draw(
            text="STOPPED",
            color="red",
            sleep_time=600
        )





#totally a test

#################
# MAIN FUNCTION #
#  (MAIN MENU)  #
#################


def main():
    stopwatch()



if __name__ == "__main__":
    main()