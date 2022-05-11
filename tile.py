import pygame
from settings import *

class Tile(pygame.sprite.Sprite): # pygame의 sprite.Sprite를 상속받아 클래스 생성
  def __init__(self, pos, groups, sprite_type, surface=pygame.Surface((TILESIZE, TILESIZE))):
    super().__init__(groups)
    self.sprite_type = sprite_type  # 스프라이트별로 정리할 수 있는 sprite_type 지정
    self.image = surface            # self.image에 들어갈 타일 표면을 지정
    if sprite_type == 'object':     # sprite_type이 오브젝트인 경우, 크기가 여러 종류이기 때문에 위치를 재조정
      self.rect = self.image.get_rect(topleft = (pos[0], pos[1] - TILESIZE)) # 크기가 128x128, 64x128 등 다 다르기 떄문에 해당하는 크기만큼 받아와진다음 좌상단의 위치로 직사각형을 생성한다
    else:
      self.rect = self.image.get_rect(topleft = pos)
    self.hitbox = self.rect.inflate(0, -10) # 기존 64x64인 rect에서 따로 hitbox를 위 아래 5px씩 좁혀진 중심은 같은 크기의 박스를 overlapping한다.
    # inflate() -> grow or shrink the rectangle size