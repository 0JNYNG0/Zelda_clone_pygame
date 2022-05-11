from csv import reader
from os import walk  # 디렉토리를 리스트형으로 읽어오게해주는 walk를 import함
import pygame

def import_csv_layout(path):  # < csv 파일을 읽어서 새로운 맵 리스트를 생성 >
  terrain_map = []
  with open(path) as level_map:  # level_map으로써 path경로의 파일을 열어 확인.
    layout = reader(level_map, delimiter = ',')  # leave_map을 ,(콤마)로 구분하여 읽어들인 뒤 layout에 저장한다.
    for row in layout:  # layout의 csv맵 한 줄row씩 뽑아 terrain_map 리스트에 리스트 형식으로 추가해준다. 
      terrain_map.append(list(row))
    return terrain_map # terrain_map 완성


def import_folder(path): # < 디렉토리 경로 내의 모든 파일들을 읽고 추가하여 파일 리스트를 생성 >
  surface_list = []

  for _, __, img_files in walk(path): # 첫 번쨰, 두 번째 인자는 필요하지 않다. 뽑아 써야하는 곳은 마지막 인자 img_files
    for image in img_files:
      full_path = path + '/' + image # 파일을 찾길 원하는 경로 path에 추가적으로 해당 디렉토리 안의 파일까지 읽어 '/'을 붙이고 연결하여 full_path를 만든다.
      image_surf = pygame.image.load(full_path).convert_alpha()
      surface_list.append(image_surf) # 디렉토리 경로 path 하나를 통해 해당 폴더 내의 모든 파일 주소를 surface_list에 추가한다.
  
  return surface_list
