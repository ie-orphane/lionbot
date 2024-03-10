import pickle, json
from discord import Colour
from datetime import datetime, timedelta, UTC
import matplotlib.pyplot as plt

rich_black = '#000814'
oxford_blue = '#001d3d'
mikado_yellow = '#ffc300'
gold = '#ffd60a'

def color_dict():
  reset = "\x1b[0m"
  bold = "\x1b[1m"
  colors_name = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
  color_dict = {}

  for i in range(8):
      color_dict[colors_name[i]] = lambda text, i=i: f"{bold}\x1b[3{str(i)}m{text}{reset}"

  return color_dict



class Const():
  data_file_path = "./data/data.pickle"
  
  emojis = {
    'Bash': '<:bash:1181688823030239262>',
    'SCSS': '<:sass:1181690282304090152>',
    'Sass': '<:sass:1181690282304090152>',
    'CSS': '<:css:1181688880735457390>',
    'HTML': '<:html:1181688836166783057>',
    'JavaScript': '<:js:1181689391551348836>',
    'Markdown': '<:markdown:1181685547308159076>',
    'Python': '<:python:1181689899649335307>',
    'Text': '<:text:1181906243107946546>'
  }

  def __init__(self):
    self.__dict__.update(color_dict())

const = Const()

class Server():
  def __init__(self, leaderboardCh, leaderboardTop, leaderboardBottom):
    self.leaderboardCh = leaderboardCh
    self.leaderboardTop = leaderboardTop
    self.leaderboardBottom = leaderboardBottom

codingServer = Server(1178711213140615229, 1181579266270449776, 1181579270070472724)
lionsServer = Server(1178675428257435658, 1181590862858301441, 1181590867446857780)
leaderboard_servers = [codingServer, lionsServer]


def leaderboard_image(template, text_color, background_color, image_name, data: dict, heading_data: dict):
    """
        - template = Literal['first', 'last']
    
        - data = [
            {
                '': '1',
                'Coder': 'Ahmed',
                'Total': '10s',
                'Languages': 'html'
            }
        ]

        - heading_data = {'count': int, 'start': str, 'end': str} / {'time': str}
    """
  
    match template:
        case 'first':
          data = data[:11][::-1]
          ybottom = -.5
          x = -1
          heading = f"ax.set_title('Week {heading_data['count']}  -  {heading_data['start']}  ~ {heading_data['end']}', pad=0, loc='center', va='top', fontsize=13, weight='bold', color=text_color)"
          
        case 'last':
          data = data[11:][::-1]
          ybottom = -1
          x = 0
          heading = f"plt.figtext(.5, .075, 'Last Update  -  {heading_data['time']}', fontsize=7.5,  ha='center', color=text_color)"


  # setting variables
    magic_height = 300
    w = 945
    h = 874
    dpi = 80
    rows = 13  # number of rows that we want
    cols = 8  # number of columns that we want

    # setting structure
    fig, ax = plt.subplots(dpi=dpi, facecolor=background_color)
    fig.set_size_inches(magic_height*w*1.5/(h*dpi), magic_height/dpi)

    ax.set_ylim(ybottom, rows)  #  y limits
    ax.set_xlim(0, cols)  #  X limits

    fig.tight_layout(rect=(0, 0, 1, .94))
    ax.axis('off')  # removing all the spines


    # iterating over each row of the dataframe and plot the text
    for index, user in enumerate(data):
        # ploting all data
        for xpos, name in [(.5, ""), (.75, "Coder"), (2.875, "Total"), (4.25, "Languages")]:
            ax.text(x=xpos, y=index + 1 + x, s=user[name], va="center", color=text_color,
                    size=8.5 if name == "Coder" else 9.5,
                    weight="bold" if name == "Coder" else "normal",
                    ha="center" if name == "" else "left")

    # Adding the headers
    for xpos, name in [(.5, ""), (.75, "Coder"), (2.875, "Total"), (4.25, "Languages")]:
        ax.text(xpos, rows - 1 + x, name, weight='bold', size=11, color=text_color)

    # Adding heading (title / footenote)
    exec(heading)

    # adds main line below the headers
    ax.plot([.25, cols - .25], [rows - 1.375 + x, rows - 1.375 + x], ls="-", lw=1, c=text_color)

    # adds main line below the data
    ax.plot([.25, cols - .25], [.5 + x, .5 + x], ls="-", lw=1, c=text_color)

    # adds multiple lines below each row
    for index in range(11):
        if index != 0:
            ax.plot([.25, cols - .2], [index + .5 + x, index + .5 + x], ls='-', lw='.375', c=text_color)

    # save the figure as an image
    fig.savefig(f'assets/{image_name}.png', format='png', dpi=h/magic_height*dpi)

    plt.close(fig)

blue = Colour.from_str('#0d6efd')
indigo = Colour.from_str('#6610f2')
purple = Colour.from_str('#6f42c1')
pink = Colour.from_str('#d63384')
red = Colour.from_str('#dc3545')
orange = Colour.from_str('#fd7e14')
yellow = Colour.from_str('#ffc107')
green = Colour.from_str('#198754')
teal = Colour.from_str('#20c997')
cyan = Colour.from_str('#0dcaf0')
black = Colour.from_str('#000')
white = Colour.from_str('#fff')
gray = Colour.from_str('#6c757d')
empty = "<:empty:1144234051947999322>"
logChannel = 1177274268577443910

class User():
  def __init__(self) -> None:
    self.full_name = ""
    self.student = True
    self.verified = False
    self.service = None
    self.session = None

  def __repr__(self) -> str:
     return f"<User full_name={self.full_name} {"student" if self.student else ""}>"


def open_file(file_path, data=None):
  file_extention = file_path.split('.')[-1]
  match file_extention:
    case 'json':
      module = json
      write_mode = 'w'
      read_mode = 'r'
    case 'pickle':
      module = pickle
      write_mode = 'wb'
      read_mode = 'rb'
  
  if data:
      with open(file_path, write_mode) as file:
        if file_extention == 'json':
          module.dump(data, file, indent=2)
        else:
          module.dump(data, file)
        return

  with open(file_path, read_mode) as file:
    return module.load(file)

def get_data(user_id: int = None):
  """
    - user_id = None -> data
    - user_id found -> user_data
    - user_id not found -> None
  """
  
  data = open_file(const.data_file_path)
  if user_id:
      if user_id in data:
          return data[user_id]
      return
  return data

def save_data(data: dict):
  open_file(const.data_file_path, data)

class Week():
  def __init__(self, data: dict) -> None:
    self.__dict__ = data
    self.readable_start = str(self.start_date)
    self.readable_end = str(self.end_date)
    self.human_readable_start = f"{self.start_date:%d %b %Y}"
    self.human_readable_end = f"{self.end_date:%d %b %Y}" 

  def __repr__(self) -> str:
     return f"<Week #{self.count} from='{self.start_date}' to='{self.end_date}'>"


def get_week(*, week_argument = 'last', end_date = None) -> Week | list:
  start_date = datetime(2023, 10, 23)
  end_date = end_date or datetime.utcnow()
  weeks: list[Week] = []

  current_date = start_date
  week_count = 1

  while current_date <= end_date:
    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    week_data = {
      'count': week_count, 
      'start_date': start_of_week.date(), 
      'end_date': end_of_week.date(), 
    }
    weeks.append(Week(week_data))
    
    current_date += timedelta(days=7)
    week_count += 1

  match week_argument:
    case 'beforelast':
      last_week = weeks[-2]
      # last_week.readable_end = f"{end_date:%Y-%m-%d}"
      return last_week
    case 'last':
      last_week = weeks[-1]
      # last_week.readable_end = f"{end_date:%Y-%m-%d}"
      return last_week
    case 'all':
      return weeks
    case _:
      return weeks[int(week_argument) - 1]
