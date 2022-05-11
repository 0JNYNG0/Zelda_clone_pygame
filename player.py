import pygame
from settings import *
from support import import_folder
from entity import Entity

class Player(Entity):  # pygame의 sprite.Sprite를 상속받아 클래스 생성
  def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic): # pos, group을 넘겨받고 초기화됨
    super().__init__(groups) 
    self.image = pygame.image.load('./Image/player.png').convert_alpha() # 이미지 로드
    self.rect = self.image.get_rect(topleft = pos) # 왼쪽 위 최상단 좌표로 사각형 지정(?)
    self.hitbox = self.rect.inflate(0, -26)  # 플레이어의 hitbox를 위아래 13씩 줄인 정도의 직사각형으로 지정

    # graphics setup
    self.import_player_assets()   # 초기화 과정에서 player_assets를 불러오기위한 함수 실행
    self.status = 'down'          # 맨 처음 게임 시작할 때 status = 'down'에서 시작

    # movement
    self.attacking = False
    self.attack_cooldown = 400  # 0.4 s
    self.attack_time = None
    self.obstacle_sprites = obstacle_sprites  # 플레이어와 충돌처리를 해주기 위한 sprite를 초기화할 떄 불러와준다.

    # weapon
    self.create_attack = create_attack
    self.destroy_attack = destroy_attack
    self.weapon_index = 0
    self.weapon = list(weapon_data.keys())[self.weapon_index] # settings.py의 weapon_data에 이름값인 key만을 불러와 해당 인덱스의 무기를 가져온다.
    self.can_switch_weapon = True       # 무기를 한 번에 한 번만 교체할 수 있게 하는 변수
    self.weapon_switch_time = None      # cooldown 계산하기 위한 시간
    self.switch_duration_cooldown = 200 # 무기 교환 cooldown

    # magic
    self.create_magic = create_magic
    self.magic_index = 0
    self.magic = list(magic_data.keys())[self.magic_index]
    self.can_switch_magic = True
    self.magic_switch_time = None

    # stats
    self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 5}
    self.health = self.stats['health'] * 0.5
    self.energy = self.stats['energy'] * 0.8
    self.exp = 123
    self.speed = self.stats['speed']

    # damage timer
    self.vulnerable = True
    self.hurt_time = None
    self.invulnerability_duration = 500

  def import_player_assets(self):
    character_path = './graphics/player/'  # 애니메이션의 full_path를 만들어주기 위한 경로의 앞 부분
    self.animations = {
      'up': [], 'down': [], 'left': [], 'right': [],
      'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
      'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []
    }

    for animation in self.animations.keys():
      full_path = character_path + animation
      self.animations[animation] = import_folder(full_path)  # full_path로 애니메이션 assets에 접근하여 self.animations 에 각 항목별로 초기화함

  def input(self):

    if not self.attacking:  
      keys = pygame.key.get_pressed() # input 함수를 업데이트 하며 사용자가 입력한 키를 받아온다.

      # movement input
      if keys[pygame.K_UP]:
        self.direction.y = -1
        self.status = 'up'
      elif keys[pygame.K_DOWN]:
        self.direction.y = 1
        self.status = 'down'
      else:
        self.direction.y = 0

      if keys[pygame.K_RIGHT]:
        self.direction.x = 1
        self.status = 'right'
      elif keys[pygame.K_LEFT]:
        self.direction.x = -1
        self.status = 'left'
      else:
        self.direction.x = 0
      # 상, 하, 좌, 우 입력 별 방향벡터x,y 변경

      # attack input
      if keys[pygame.K_SPACE]:
        self.attacking = True
        self.attack_time = pygame.time.get_ticks()
        self.create_attack()  # 무기 생성 함수 실행

      # magic input
      if keys[pygame.K_LCTRL]:
        self.attacking = True
        self.attack_time = pygame.time.get_ticks()
        style = list(magic_data.keys())[self.magic_index]
        strength = list(magic_data.values())[self.magic_index]['strength'] + self.stats['magic']
        cost = list(magic_data.values())[self.magic_index]['cost']
        self.create_magic(style, strength, cost)

      # weapon change input
      if keys[pygame.K_q] and self.can_switch_weapon:                # 무기 교체
        self.can_switch_weapon = False                               # 한 번만 무기 교체가 가능하도록 제한
        self.weapon_switch_time = pygame.time.get_ticks()

        if self.weapon_index < len(list(weapon_data.keys())) - 1:    # 무기index를 벗어나지 않도록 제한
          self.weapon_index += 1
        else:
          self.weapon_index = 0                                      # index가 끝나면 loop

        self.weapon = list(weapon_data.keys())[self.weapon_index] 

      # magic change input
      if keys[pygame.K_e] and self.can_switch_magic:                
        self.can_switch_magic = False                              
        self.magic_switch_time = pygame.time.get_ticks()

        if self.magic_index < len(list(magic_data.keys())) - 1:   
          self.magic_index += 1
        else:
          self.magic_index = 0                                  

        self.magic = list(magic_data.keys())[self.magic_index]

  def get_status(self):
    
    # idle status
    if self.direction.x == 0 and self.direction.y == 0:
      if not 'idle' in self.status and not 'attack' in self.status:  # status가 idle이 됐을 때 한 번만 status가 적용되도록 함
        # idle이 status 내에 없으면 + _idle을 붙여줌(즉, 딱 한번)
        self.status = self.status + '_idle'
    
    if self.attacking:
      self.direction.x = 0
      self.direction.y = 0
      if not 'attack' in self.status: # 공격할 때
        if 'idle' in self.status:
          self.status = self.status.replace('_idle', '_attack') # _idle 상태를 _attack 상태로 전환
        else:
          self.status = self.status + '_attack' # _idle이 아닌경우 그냥 _attack를 한 번만 붙도록 함
    else:
      if 'attack' in self.status: # attack이 status에 남아있을 때
        self.status = self.status.replace('_attack', '') # 공격이 끝나면 공격을 풀어주기 위해 ''로 바꿔준다

  def cooldowns(self):
    current_time = pygame.time.get_ticks()

    if self.attacking:
      if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']: # 공격하고 난 뒤 지난 시간이 쿨타임 시간보다 많거나 같아질 경우 다시 공격 가능
        self.attacking = False
        self.destroy_attack()  # 무기 삭제 함수 실행

    if not self.can_switch_weapon:
      if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
        self.can_switch_weapon = True   # 쿨타임이 끝나면 다시 무기 교체가 가능

    if not self.can_switch_magic:
      if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
        self.can_switch_magic = True   # 쿨타임이 끝나면 다시 마법 교체가 가능

    if not self.vulnerable:
      if current_time - self.hurt_time >= self.invulnerability_duration:
        self.vulnerable = True

  def animate(self):
    animation = self.animations[self.status] # 초기화해둔 애니메이션을 토대로 현재 status에 맞는 animation을 불러오게됨

    # loop over the frame index
    self.frame_index += self.animation_speed 
    if self.frame_index >= len(animation): # 애니메이션 loop를 해주기 위함
      self.frame_index = 0 # 정해진 애니메이션 길이가 있으므로 frame이 넘어가면 0으로 초기화

    # set the image
    self.image = animation[int(self.frame_index)]
    self.rect = self.image.get_rect(center = self.hitbox.center)

    # flicker
    if not self.vulnerable:
      alpha = self.wave_value()
      self.image.set_alpha(alpha)
    else:
      self.image.set_alpha(255)

  def get_full_weapon_damage(self):
    base_damage = self.stats['attack']
    weapon_damage = weapon_data[self.weapon]['damage']
    return base_damage + weapon_damage

  def update(self): # update라는 이름의 함수는 만든것이 아닌 자체 지정된 api 함수. 자동적으로 디스플레이 업데이트가 되면서 이 함수도 같이 실행됨.
    self.input()  # FPS 초당 60번 반복하며 사용자의 입력을 받음.
    self.cooldowns()
    self.get_status()
    self.animate()
    self.move(self.speed)  # 입력받은대로 플레이어 스프라이트를 움직임.