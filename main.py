from __future__ import annotations
from abc import ABC, abstractmethod
import pygame
from pygame import Surface, Rect
from pygame.sprite import Sprite, Group
from pygame.event import Event
from pygame.key import ScancodeWrapper
#region          Incializar
pygame.init()
#endregion

#colisões bola com o player
#colisões bola com o tijolo

#region          Organizar dados

default_colors:dict[str,tuple[int,int,int]] = {
    "red"   :(255, 0, 0),
    "green" :(0, 255, 0),
    "blue"  :(0, 0, 255),
    
    "yellow":(255,255,0),
    "purple":(255,0,255),
    
    "black" :(0, 0, 0),
    "white" :(255,255,255),
}

#region          Classes
class Window:
    def __init__(self,tamanho:tuple[int,int],title:str=""):
        self._tamanho = tamanho
        self._largura = tamanho[0]
        self._altura  = tamanho[1]
        self._title   = title
        self._janela  = self.criar_janela()

    @property
    def janela(self)->Surface:
        return self._janela
    
    @property
    def largura(self)-> int:
        return self._largura
    
    @property
    def altura(self):
        return self._altura

    def criar_janela(self)-> Surface:
        janela = pygame.display.set_mode(self._tamanho)
        pygame.display.set_caption("Brick Break")
        return janela

class GameMaster:
    def __init__(self,
                 tamanho_tela:tuple[int,int], titulo_tela:str,
                 brickspLine:int, lines:int ,
                 player_hspd:int = int(3)   , player_color:tuple[int, int, int] = default_colors["blue"],
                 bola_spd:list[int] = [3,-3] , bola_color:tuple[int,int,int] = default_colors["white"],
                 ) -> None:

        self._game_is_end:bool = False
        self._points:int = 0

        self._element_tela   = Window(tamanho_tela, titulo_tela)
        self._element_player = self.player_creator(player_hspd,player_color)
        self._element_bola   = self.ball_creator(bola_spd,bola_color)

        self._element_bricks_list = self.brick_creator(brickspLine, lines)

    #region propertys
    @property
    def tela(self) -> Window:
        return self._element_tela
    
    @property
    def player(self) -> Player:
        return self._element_player
    
    @property
    def ball(self) -> Bola:
        return self._element_bola
    
    @property
    def bricks_list(self) -> list[Bloco]:
        return self._element_bricks_list
    
    @property
    def game_is_end(self) -> bool:
        return self._game_is_end
    
    @property
    def points(self) -> int:
        return self._points
    #endregion 
    
    def verificar_se_perdeu(self)->bool:
        bola = self.ball
        return bola.y + bola.height + bola.speed[1] >= self.tela.altura

    def verificar_se_ganhou(self)->bool:
        return not self._element_bricks_list

    def end_game(self):
        self._game_is_end = True
    
    def addPoint(self):
        self._points += 1

    def draw_elements (self):
        self.tela.janela.fill(default_colors["black"])
        self.player.draw()

        for b in self._element_bricks_list:
            b.draw()
        
        self.ball.draw()


    def player_creator(self,player_hspd:int, player_color:tuple[int, int, int])->Player:
        largura = self.tela.largura
        altura = self.tela.altura

        #region          player CFGs
        player_width  = int(largura / 5)
        player_height = int(altura / 40)

        player_x = int(largura / 2)
        player_y = int(altura * 0.9)

        #endregion
        return Player(player_x, player_y, player_width, player_height ,self.tela, player_hspd, player_color)

    def ball_creator(self,bola_spd:list[int] ,bola_color:tuple[int, int, int])->Bola:
        largura = self.tela.largura
        altura = self.tela.altura

        #region          ball CFGs
        ball_side = int(altura/80)
        ball_height = ball_side
        ball_width = ball_side

        ball_x = int(largura/ 2)
        ball_y = int(altura / 2)

        #endregion
        return Bola(ball_x, ball_y, ball_width, ball_height, self.tela, bola_spd, bola_color)

    def brick_creator(self, bricks_per_line:int, lines:int) -> list[Bloco]:
        
        tela = self.tela
        largura = tela.largura

        space_x = int(largura/80)
        space_y = space_x

        brickswidth  = int(largura/bricks_per_line - int(space_x/2))
        bricksheight = int(brickswidth/2 - int(space_y/2))
        
        bricks = []
        for l in range(lines):
            for b in range(bricks_per_line):
                bricks.append(Bloco(b * (brickswidth  + int(space_x/2) + 3),
                                    l * (bricksheight + int(space_y/2)    ),
                                    brickswidth, bricksheight, tela  )    )
                
        return bricks

    def check_collision_BallxPlayer(self):
        bola = self.ball
        player =  self.player

        if bola.body.colliderect(player.body):
                if abs(bola.body.bottom - player.body.top) < player.height/4:
                    bola.invert_vertical_move()
                else:
                    bola.invert_horizontal_move()

    def check_collision_BallxBrick(self):
        bola = self.ball
        for b in self.bricks_list:
            if bola.body.colliderect(b.body):
                if abs(bola.body.bottom - b.body.top) < 10:
                    bola.invert_vertical_move()
                elif abs(bola.body.top - b.body.bottom) < 10:
                    bola.invert_vertical_move()
                else:
                    bola.invert_horizontal_move()

                self.bricks_list.remove(b)
                self.addPoint()
                break

    def check_collision_BallxParede(self):
        # bola   ->  parede
        bola = self.ball
        tela = self.tela

        largura_bola = bola.width
        largura_tela = tela.largura

        #transformar speed em hspd e vspd
        if (bola.x + largura_bola + bola.speed[0] >= largura_tela) or (bola.x + bola.speed[0] <= 0):
            bola.invert_horizontal_move()

        if (bola.y + bola.speed[1] <= 0):
            bola.invert_vertical_move()

    def execute_colisions(self):
        self.check_collision_BallxBrick()
        self.check_collision_BallxPlayer()
        self.check_collision_BallxParede()
    
    def execute_elements_movement(self):
        self.ball.bola_move()
        self.player.player_move()

    def check_win_or_lose(self):
        perdeu = self.verificar_se_perdeu()
        if perdeu:    
            print("You Lose!!!") 
            print(f"Points:{self.points}")
            self.end_game()
            
        ganhou = self.verificar_se_ganhou()
        if ganhou:    
            print("You Win!!!") 
            print(f"Points:{self.points}")
            self.end_game()

    def core_loop(self) -> None:

        while not self.game_is_end:
            
            self.execute_elements_movement()
            self.execute_colisions()

            self.check_win_or_lose()

            for user_event in pygame.event.get():
                if user_event.type == pygame.QUIT:
                    self.end_game()
            
            self.draw_elements()
            clock = pygame.time.Clock()
            clock.tick(120)
            pygame.display.flip()


class Game_rectangle_element(ABC):
    @abstractmethod
    def __init__(self, x:int , y:int, tela:Window, width:int, height:int, color:tuple[int,int,int] = default_colors["white"]) -> None:
        pass

    @property
    @abstractmethod
    def body(self) -> Rect:
        pass

    @abstractmethod
    def draw(self):
        pass


class Bola(Game_rectangle_element):
    def __init__(self, x:int , y:int, width:int, height:int, tela:Window, spd:list[int] = [1,-1],color:tuple[int,int,int] = default_colors["white"]) -> None:
        self._x = x
        self._y = y

        self._tela = tela

        self._width  = width
        self._height = height

        self._body = pygame.Rect(self._x,self._y,self._width,self._height)

        self._color  = color
        self._speed  = spd                   
    
    @property
    def speed(self)->list[int]:
        return self._speed
    @speed.setter
    def speed(self,spd:list[int]):
        self._speed = spd

    @property
    def tela(self)->Window:
        return self._tela
    
    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y
    @property
    def height(self) -> int:
        return self._height

    @property
    def width(self) -> int:
        return self._width
    
    @property
    def color(self)-> tuple[int, int, int]:
        return self._color
    
    @property
    def body(self) -> Rect:
        return self._body
    
    def bola_move(self):

        self._y += self._speed[1]
        self._x += self._speed[0]

        self.body.x = self._x
        self.body.y = self._y

    def invert_horizontal_move(self):
        self._speed[0] *=-1
    
    def invert_vertical_move(self):
        self._speed[1] *=-1

    def draw(self):
       pygame.draw.rect(self.tela.janela,self.color, self.body)

class Player(Game_rectangle_element):
    def __init__(self ,
                 x:int,
                 y:int,
                 width :int    ,
                 height:int    ,
                 tela  :Window ,
                 hspd  :int = 1,
                 color :tuple[int,int,int] = default_colors["white"],
                 ) -> None:
        
        self._x = x
        self._y = y

        self._tela   = tela

        self._width  = width
        self._height = height

        self._hspd   = hspd

        self._body   = pygame.Rect(self._x,self._y,self._width,self._height)

        self._color  = color
    #mudar o p.height para ser proporcional ao tamanho da tela.
    #usar essa proporção para medir a colisão lateral da bola.
    @property
    def color(self) -> tuple[int, int, int]:
        return self._color
    
    @property
    def tela(self) -> Window:
        return self._tela
    
    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y
    
    @property
    def height(self) -> int:
        return self._height

    @property
    def width(self) -> int:
        return self._width
    
    @property
    def speed(self) -> int:
        return self._hspd
    
    @property
    def body(self) -> Rect:
        return self._body

    def player_move(self):
        keys: ScancodeWrapper = pygame.key.get_pressed()
            
        if keys[pygame.K_RIGHT]:
            if (self.body.x + self._width + self._hspd) <= self.tela.largura:
                self._x += self._hspd
                self.body.x = self._x
            else: 
                while (self.body.x + self._width) < self.tela.largura:
                    self._x += 1
                    self.body.x = self._x

        if keys[pygame.K_LEFT]:
            if (self.body.x - self._hspd) >= 0:
                self._x -= self._hspd
                self.body.x = self._x
            else: 
                while self.body.x > 0:
                    self._x -= 1
                    self.body.x = self._x
    
    def draw(self):
        pygame.draw.rect(self.tela.janela,self._color, self._body)

class Bloco(Game_rectangle_element):
    def __init__(self, x:int, y:int, width:int, height:int, tela:Window, color:tuple[int,int,int] = default_colors["green"]) -> None:
        self._x = x
        self._y = y

        self._tela = tela
        self._color = color

        self._width  = width
        self._height = height

        self._body   = pygame.Rect(self._x,self._y,self._width,self._height)

    @property
    def body(self) -> Rect:
        return self._body
    
    @property
    def tela(self)->Window:
        return self._tela

    def draw(self):
        pygame.draw.rect(self.tela.janela,self._color,self.body)

#endregion

#endregion

#region          CFGs

#--------------# Tela CFGs #--------------#
tamanho_tela = (800,800)
titulo_tela = "Brick Breaker"

#----------# Bricks list CFGs #-----------#
brickspLine = 12
lines = 6

#endregion

GM = GameMaster(tamanho_tela, titulo_tela, brickspLine, lines)
GM.core_loop()

pygame.quit()