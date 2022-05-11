import pygame
from magic import MagicPlayer
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer

class Level:
  def __init__(self):

    # get the display surface
    self.display_surface = pygame.display.get_surface() # 현재 설정된 디스플레이 표면에 대한 참조 가져오기
    
    # sprite group setup - 여러 sprite 객체를 보유하고 관리하는 컨테이너
    self.visible_sprites = YSortCameraGroup() ### pygame.sprite.Group() 
      # 눈에 보이는 스프라이트 그룹화
    self.obstacle_sprites = pygame.sprite.Group() # 장애물 역할 스프라이트 그룹화

# 먼저 각 sprite마다 group을 지정해주자.
# 그래야 ground타일은 ground그룹에 tree면 tree_group에 속해야 플레이어랑 부딪히는 
# sprite가 어디 그룹에 속해있는지 알고 그에 따른 반응을 구현해야하기 때문이다.

    # attack sprites
    self.current_attack = None
    self.attack_sprites = pygame.sprite.Group()
    self.attackable_sprites = pygame.sprite.Group()

    # sprite setup
    self.create_map()  # 아래 함수를 실행

    # user interface
    self.ui = UI()

    # particles
    self.animation_player = AnimationPlayer()
    self.magic_player = MagicPlayer(self.animation_player)

  def create_map(self): # settings.py의 WORLD_MAP을 볼러옴
    layouts = {  # 순수 문자열 리스트 집합으로 만들어진 맵 정보
        'boundary': import_csv_layout('./map/map_FloorBlocks.csv'),
        'grass': import_csv_layout('./map/map_Grass.csv'),
        'object': import_csv_layout('./map/map_Objects.csv'),
        'entities': import_csv_layout('./map/map_Entities.csv')
    }
    
    graphics = {  # 지정된 폴더 경로안의 그래픽 스프라이트
        'grass': import_folder('./graphics/grass'),
        'objects': import_folder('./graphics/objects')
    }
# 'boundary' -> style , import_csv_~~ -> layout
    for style, layout in layouts.items():  # layouts의 원소들을 빼와 지정된 형식인 style과 csv파일 검색 후 맵 정보를 가져옴
      for row_index, row in enumerate(layout): # enumerate() -> 불러온 원소에 대해 해당 인덱스와 원소에 차례대로 접근하게 도와줌:: row = 맵정보 레이아웃 한줄
        for col_index, col in enumerate(row): # col = 맵 한줄의 타일 한 칸 정보
          if col != '-1': # -1 은 플레이어가 다닐 수 있는 길이다.
            x = col_index * TILESIZE  # 각 index를 불러온 뒤 TILESIZE 한 칸에 맞게 좌표 설정
            y = row_index * TILESIZE  # 타일 한개당 위치를 좌표로 본다
            if style == 'boundary':
              Tile((x,y), [self.obstacle_sprites], 'invisible') # boundary. 움직임을 막는 경계선은 보이면 안되므로 obstacle_sprites만 적용 타일 생성
            if style == 'grass':
              random_grass_image = choice(graphics['grass'])  # random 모듈 내 choice함수를 사용하여 graphics/grass 폴더 안 스프라이트를 랜덤으로 지정 후 타일 생성
              Tile(
                (x,y),
                [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites], 
                'grass', 
                random_grass_image)
            if style == 'object':
              surf = graphics['objects'][int(col)]  # 자동적으로 128x128인 스프라이트는 TILESIZE가 128인 surf로 생성됨
              Tile((x,y), [self.visible_sprites, self.obstacle_sprites], 'object', surf)        
            if style == 'entities':
              if col == '394':
                self.player = Player(
                  (x, y), 
                  [self.visible_sprites], 
                  self.obstacle_sprites, 
                  self.create_attack, 
                  self.destroy_attack,
                  self.create_magic
                )
              else:
                if col == '390': monster_name = 'bamboo'
                elif col == '391': monster_name = 'spirit'
                elif col == '392': monster_name = 'raccoon'
                else: monster_name = 'squid'
                Enemy(
                  monster_name,
                  (x, y), 
                  [self.visible_sprites, self.attackable_sprites], 
                  self.obstacle_sprites,
                  self.damage_player,
                  self.trigger_death_particles)
            ## -1인 곳을 제외한 나머지 스프라이트 위치에 각 style을 비교 후 일치하는 타일에 객체를 생성하여 타일을 보여주도록 한다.

    #     if col == 'x': # 장애물
    #       Tile((x, y), [self.visible_sprites, self.obstacle_sprites]) # 위치와 어떤 그룹에 속하는지 지정 객체 생성
    #     if col == 'p': # 플레이어
    #       self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites) # 위치와 어떤 그룹에 속하는지 지정 객체 생성

  def create_attack(self):
    self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])  # self.current_attack 변수에 Weapon 객체를 생성

  def create_magic(self, style, strength, cost):
    if style == 'heal':
      self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])
    
    if style == 'flame':
      self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])

  def destroy_attack(self):       # 생성한 무기 삭제 함수
    if self.current_attack:       # 생성한 무기 객체가 존재한다면 True
      self.current_attack.kill()
    self.current_attack = None

  def player_attack_logic(self):
    if self.attack_sprites:
      for attack_sprite in self.attack_sprites:
        # attackable_sprites의 스프라이트들이 Weapon인 attack_sprite와 겹칠경우 모든 스프라이트를 리스트로 반환한다.
        collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False) # True일 경우 반환된 모든 스프라이트를 해당 그룹에서 삭제함.
        if collision_sprites:
          for target_sprite in collision_sprites:
            if target_sprite.sprite_type == 'grass': # grass만 떄렸을 경우 바로 사라지게 만든다
              pos = target_sprite.rect.center
              offset = pygame.math.Vector2(0, 75)
              for leaf in range(randint(3, 6)):
                self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])
              target_sprite.kill()
            else:
              target_sprite.get_damage(self.player, attack_sprite.sprite_type)
            
  def damage_player(self, amount, attack_type):
    if self.player.vulnerable:
      self.player.health -= amount
      self.player.vulnerable = False
      self.player.hurt_time = pygame.time.get_ticks()
      self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])

  def trigger_death_particles(self, pos, particle_type):
    self.animation_player.create_particles(particle_type, pos, self.visible_sprites)

  def run(self): # 초당 60FPS 반복되는 level.py의 run 함수

    # update and draw the game
    self.visible_sprites.custom_draw(self.player) ###self.visible_sprites.draw(self.display_surface) 
          # visible스프라이트를 모두 화면에 그리기
    self.visible_sprites.update()
    self.visible_sprites.enemy_update(self.player)
    self.player_attack_logic()
    self.ui.display(self.player)

class YSortCameraGroup(pygame.sprite.Group):  # 플레이어 카메라 클래스
  def __init__(self):

    # general setup
    super().__init__()
    self.display_surface = pygame.display.get_surface()
    self.half_width = self.display_surface.get_size()[0] // 2   # 카메라의 위치를 잡기위한 화면의 절반넓이
    self.half_height = self.display_surface.get_size()[1] // 2  # 카메라의 위치를 잡기위한 화면의 절반높이
    self.offset = pygame.math.Vector2()  # 카메라 오프셋 벡터

    #creating the floor
    self.floor_surf = pygame.image.load('./graphics/tilemap/ground.png').convert() # 맵 기본 floor이미지를 로드하여 생성
    self.floor_rect = self.floor_surf.get_rect(topleft = (0, 0))                   # 불러온 기본 맵 floor를 상단좌측 맨 끝에 rect로 지정

  def custom_draw(self, player):

    # getting the offset 
    self.offset.x = player.rect.centerx - self.half_width   # 플레이어 위치 중심을 기준으로 카메라 오프셋 x, y 좌표를 설정
    self.offset.y = player.rect.centery - self.half_height

    #drawing the floor
    floor_offset_pos = self.floor_rect.topleft - self.offset  # 플레이어 위치 중심을 기준으로 맵의 오프셋 좌표 설정
    self.display_surface.blit(self.floor_surf, floor_offset_pos)  # 설정한 위치에 불러온 floor맵을 blit으로 보여줌


    ###for sprite in self.sprites(): # .sprites() -> 해당 그룹에 포함된 스프라이트들의 리스트를 받아옴
    for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):  # sprite.rect의 centery값을 정렬한 sprite 순서대로 반복.(위에서 오른아래로 진행)
      offset_pos = sprite.rect.topleft - self.offset   # 카메라 오프셋 위치에 대해 스프라이트의 상대적 위치를 구한다
      self.display_surface.blit(sprite.image, offset_pos)  # 구한 스프라이트의 위치로 해당 스프라이트를 blit하여 보여준다.
      # 반복되는 해당 원리로 플레이어 중심 기준으로 주변 스프라이트들이 그에 따라 맞춰 움직여진다.

  def enemy_update(self, player):
    enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
    for enemy in enemy_sprites:
      enemy.enemy_update(player)