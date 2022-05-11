import pygame, sys 
from settings import *
from level import Level

class Game:
  def __init__(self):
    # general setup
    pygame.init() # pygame 초기화 단계 (필수)
    self.screen = pygame.display.set_mode((WIDTH, HEIGHT)) # set_mode를 통한 디스플레이 초기화
    pygame.display.set_caption('Zelda') # set_caption을 통한 제목 초기화
    self.clock = pygame.time.Clock() # 클락 객체를 생성 -> .tick()을 통해 FPS설정가능

    self.level = Level()  # Level클래스 객체 level 생성

  def run(self):  # 게임을 실행해주기 위한 run 함수
    while True:
      for event in pygame.event.get():
        if event.type == pygame.QUIT: # 게임 종료 버튼 클릭
          pygame.quit()
          sys.exit()

      self.screen.fill('black')  # 지정한 화면을 'black'으로 채움
      self.level.run()  # level.py의 run() 실행 -> [스프라이트 화면에 그리기]
      pygame.display.update()  # ()안에 아무것도 없을 경우, 전체 surface업데이트 == flip()
      self.clock.tick(FPS) # .tick을 이용한 초당 FPS번 루프 실행

if __name__ == '__main__': # 파이썬 Main문 실행
  game = Game()  # Game 클래스 객체 game 생성
  game.run()  # 게임 실행을 알리는 run()
