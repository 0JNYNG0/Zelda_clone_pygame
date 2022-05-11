import pygame

class Weapon(pygame.sprite.Sprite):
  def __init__(self, player, groups):
    super().__init__(groups)
    self.sprite_type = 'weapon'
    direction = player.status.split('_')[0]  # Only pick one -> right, left, top, bottom
    

    # graphic
    full_path = f'./graphics/weapons/{player.weapon}/{direction}.png'  # weapon스프라이트 경로 가져오기 from player.weapon, direction
    self.image = pygame.image.load(full_path).convert_alpha()

    # placement
    if direction == 'right':
      self.rect = self.image.get_rect(midleft = player.rect.midright + pygame.math.Vector2(0, 16))
    elif direction == 'left':
      self.rect = self.image.get_rect(midright = player.rect.midleft + pygame.math.Vector2(0, 16))
    elif direction == 'down':
      self.rect = self.image.get_rect(midtop = player.rect.midbottom + pygame.math.Vector2(-10, 0))
    else:
      self.rect = self.image.get_rect(midbottom = player.rect.midtop + pygame.math.Vector2(-10, 0))
    # 플레이어 기준 바로 옆, 위, 아래에 무기를 나타내기 위해 해당 위치에 get_rect함. -> 객체가 생성될 때 맵에 무기가 보여짐.