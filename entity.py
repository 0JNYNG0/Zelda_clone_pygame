import pygame
from math import sin

class Entity(pygame.sprite.Sprite):  # Player와 Enemy의 중복을 최소화하기위해 통틀어서 관리하는 Entity 클래스이다
  def __init__(self, groups):
    super().__init__(groups)
    self.frame_index = 0
    self.animation_speed = 0.15
    self.direction = pygame.math.Vector2()

  def move(self, speed):
    if self.direction.magnitude() != 0: # magnitude(규모) -> vector Length?
      self.direction = self.direction.normalize() # 방향은 같지만 길이는 1인 벡터를 반환(normalize)
      # 여러 방향을 움직일때 속도가 중첩되는것을 막기 위한, 속도 1인 벡터를 받아와 원래의 속도를 유지하도록 함.

    ###self.rect.x ###self.rect.y -> hitbox.x or y
    self.hitbox.x += self.direction.x * speed # 플레이어의 (벡터 * 속도)로 player.rect의 위치를 옮김
    self.collision('horizontal')
    self.hitbox.y += self.direction.y * speed
    self.collision('vertical')
    ###self.rect.center += self.direction * speed
    self.rect.center = self.hitbox.center

  def collision(self, direction):
    if direction == 'horizontal':
      for sprite in self.obstacle_sprites:
        if sprite.hitbox.colliderect(self.hitbox):  # 해당 obstacle 스프라이트가 플레이어의 rect와 겹치는지 판단
          if self.direction.x > 0: # moving right
            self.hitbox.right = sprite.hitbox.left
          if self.direction.x < 0: # moving left
            self.hitbox.left = sprite.hitbox.right
    ### 위 아래 모든 rect -> hitbox
    if direction == 'vertical':
      for sprite in self.obstacle_sprites:
        if sprite.hitbox.colliderect(self.hitbox):  # 해당 obstacle 스프라이트가 플레이어의 rect와 겹치는지 판단
          if self.direction.y > 0: # moving down
            self.hitbox.bottom = sprite.hitbox.top
          if self.direction.y < 0: # moving up
            self.hitbox.top = sprite.hitbox.bottom

  def wave_value(self):
    value = sin(pygame.time.get_ticks())
    if value >= 0: 
      return 255
    else: 
      return 0