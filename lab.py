#!/usr/bin/env python3

##################
# Game Constants #
##################

# other than TILE_SIZE, feel free to move, modify, or delete these constants as
# you see fit.

TILE_SIZE = 128

# vertical movement
GRAVITY = -9
MAX_DOWNWARD_SPEED = 48
PLAYER_JUMP_SPEED = 62
PLAYER_JUMP_DURATION = 3
PLAYER_BORED_THRESHOLD = 60

# horizontal movement
PLAYER_DRAG = 6
PLAYER_MAX_HORIZONTAL_SPEED = 48
PLAYER_HORIZONTAL_ACCELERATION = 16


# the following maps single-letter strings to the name of the object they
# represent, for use with deserialization in Game.__init__.
SPRITE_MAP = {
    "p": "player",
    "c": "cloud",
    "=": "floor",
    "B": "building",
    "C": "castle",
    "u": "cactus",
    "t": "tree",
}


##########################
# Classes and Game Logic #
##########################


class Rectangle:
    """
    A rectangle object to help with collision detection and resolution.
    """

    def __init__(self, x, y, w, h):
        """
        Initialize a new rectangle.

        `x` and `y` are the coordinates of the bottom-left corner. `w` and `h`
        are the dimensions of the rectangle.
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def intersects(self, other):
        """
        Check whether `self` and `other` (another Rectangle) overlap.

        Rectangles are open on the top and right sides, and closed on the
        bottom and left sides; concretely, this means that the rectangle
        [0, 0, 1, 1] does not intersect either of [0, 1, 1, 1] or [1, 0, 1, 1].
        """
        xOverLap=False
        yOverLap=False
        if self.x<other.x:
            if self.x+self.w>other.x:
                xOverLap=True
        else:
            if other.x+other.w>self.x:
                xOverLap=True
        if self.y<other.y:
            if self.y+self.h>other.y:
                yOverLap=True
        else:
            if other.y+other.h>self.y:
                yOverLap=True
        return xOverLap and yOverLap

    @staticmethod
    def translation_vector(r1, r2):
        """
        Compute how much `r2` needs to move to stop intersecting `r1`.

        If `r2` does not intersect `r1`, return `None`.  Otherwise, return a
        minimal pair `(x, y)` such that translating `r2` by `(x, y)` would
        suppress the overlap. `(x, y)` is minimal in the sense of the "L1"
        distance; in other words, the sum of `abs(x)` and `abs(y)` should be
        as small as possible.

        When two pairs `(x1, y1)` and `(x2, y2)` are tied in terms of this
        metric, return the one whose first element has the smallest
        magnitude.
        """
        temp=Rectangle(r1.x,r1.y,r1.w,r1.h)
        if temp.intersects(r2) is False:
            return None
        moveLeft=r2.x-r1.x+r2.w
        moveRight=r1.x+r1.w-r2.x
        moveUp=r1.y-r2.y+r1.h
        moveDown=r2.y-r1.y+r2.h
        coor=[]
        if moveLeft<moveRight:
            coor.append(-moveLeft)
        else:
            coor.append(moveRight)
        if moveDown<moveUp:
            coor.append(-moveDown)
        else:
            coor.append(moveUp)
        if abs(coor[0])<abs(coor[1]):
            return (coor[0],0)
        else:
            return (0,coor[1])
        
class obj:
    def __init__(self,obj_type,position,vert_velocity=0,hor_velocity=0,hor_accel=0,player_texture=None,idle_time=None):
        self.type=obj_type
        self.vert_velocity=vert_velocity
        self.hor_velocity=hor_velocity
        self.position=position
        self.hor_accel=hor_accel
        self.texture=player_texture
        self.idle_time=idle_time

class Game:
    def __init__(self, level_map):
        """
        Initialize a new game, populated with objects from `level_map`.

        `level_map` is a 2D array of 1-character strings; all possible strings
        (and some others) are listed in the SPRITE_MAP dictionary.  Each
        character in `level_map` corresponds to a sprite of size `TILE_SIZE *
        TILE_SIZE`.

        This function is free to store `level_map`'s data however it wants.
        For example, it may choose to just keep a copy of `level_map`; or it
        could choose to read through `level_map` and extract the position of
        each sprite listed in `level_map`.

        Any choice is acceptable, as long as it works with the implementation
        of `timestep` and `render` below.
        """
        height=len(level_map)*128
        sprite_location={
            'p':[],
            '=':[],
            'B':[],
            'u':[],
            'C':[],
            'c':[],
            't':[]
        }
        for row,string in enumerate(level_map):
            for col,item in enumerate(string):
                if item!=' ':
                    if item!='p':
                        sprite_location[item].append(obj(item,(128*(col),height-128*(row+1))))
                    else:
                        sprite_location[item].append(obj(item,(128*(col),height-128*(row+1)),player_texture='slight_smile',idle_time=0))
        self.item_loc=sprite_location
        self.progress='ongoing'
    def timestep(self, keys):
        """
        Simulate the evolution of the game state over one time step.  `keys` is
        a list of currently pressed keys.
        """
        if self.progress=='ongoing':
            static_obj={'=','t','B','c','C','u'}
            for key in keys: #read the player inputs and set values to player
                if key=='up':
                    self.item_loc['p'][0].vert_velocity=PLAYER_JUMP_SPEED
                if key=='left':
                    self.item_loc['p'][0].hor_accel=-PLAYER_HORIZONTAL_ACCELERATION
                else:
                    self.item_loc['p'][0].hor_accel=PLAYER_HORIZONTAL_ACCELERATION
            self.item_loc['p'][0].hor_velocity+=self.item_loc['p'][0].hor_accel
            self.item_loc['p'][0].hor_accel=0
            if self.item_loc['p'][0].hor_velocity>0:
                if self.item_loc['p'][0].hor_velocity<=6:
                    self.item_loc['p'][0].hor_velocity=0
                else:
                    self.item_loc['p'][0].hor_velocity-=6
            else:
                if self.item_loc['p'][0].hor_velocity>=-6:
                    self.item_loc['p'][0].hor_velocity=0
                else:
                    self.item_loc['p'][0].hor_velocity+=6
            if abs(self.item_loc['p'][0].hor_velocity)>PLAYER_MAX_HORIZONTAL_SPEED:
                if self.item_loc['p'][0].hor_velocity<0:
                    self.item_loc['p'][0].hor_velocity=-PLAYER_MAX_HORIZONTAL_SPEED
                else:
                    self.item_loc['p'][0].hor_velocity=PLAYER_MAX_HORIZONTAL_SPEED
            for obj_type in self.item_loc: #Gravity on dynamic obj
                if obj_type not in static_obj:
                    for item in self.item_loc[obj_type]:
                        new_velocity=item.vert_velocity+GRAVITY
                        if new_velocity<-MAX_DOWNWARD_SPEED:
                            item.vert_velocity=-MAX_DOWNWARD_SPEED
                        else:
                            item.vert_velocity=new_velocity
                        temp_pos=(item.position[0],item.position[1]+item.vert_velocity)
                        item.position=temp_pos
            self.item_loc['p'][0].position=(self.item_loc['p'][0].position[0]+self.item_loc['p'][0].hor_velocity,self.item_loc['p'][0].position[1])
            dynamic_list=['p']#resolves collision positions
            for obj_type in dynamic_list:
                for dynam in self.item_loc[obj_type]:
                    for static_type in static_obj:
                        for stat in self.item_loc[static_type]:
                            r1=Rectangle(stat.position[0],stat.position[1],128,128)
                            r2=Rectangle(dynam.position[0],dynam.position[1],128,128)
                            change=Rectangle.translation_vector(r1,r2)
                            if change is not None and change[0]==0:
                                if static_type=='C':
                                    self.progress='victory'
                                    dynam.texture='partying_face'
                                if static_type=='u':
                                    print('done')
                                    self.progress='defeat'
                                    dynam.texture='injured'
                                xVal=dynam.position[0]+change[0]
                                yVal=dynam.position[1]+change[1]
                                dynam.position=(xVal,yVal)
                                if change[1]>0 and dynam.vert_velocity>0 or change[1]<0 and dynam.vert_velocity<0:
                                    pass
                                else:
                                    dynam.vert_velocity=0
            for obj_type in dynamic_list:
                for dynam in self.item_loc[obj_type]:
                    for static_type in static_obj:
                        for stat in self.item_loc[static_type]:
                            r1=Rectangle(stat.position[0],stat.position[1],128,128)
                            r2=Rectangle(dynam.position[0],dynam.position[1],128,128)
                            change=Rectangle.translation_vector(r1,r2)
                            if change is not None:
                                if static_type=='C':
                                    self.progress='victory'
                                    dynam.texture='partying_face'
                                if static_type=='u':
                                    print('done2')
                                    self.progress='defeat'
                                    dynam.texture='injured'
                                xVal=dynam.position[0]+change[0]
                                yVal=dynam.position[1]+change[1]
                                dynam.position=(xVal,yVal)
                                if change[0]>0 and dynam.hor_velocity>0 or change[0]<0 and dynam.hor_velocity<0:
                                    pass
                                else:
                                    dynam.hor_velocity=0
            if self.item_loc['p'][0].position[1]<-128:
                print('done')
                self.progress='defeat'
                self.item_loc['p'][0].texture='injured'
            if self.progress=='ongoing':
                if not keys:
                    if self.item_loc['p'][0].idle_time>=PLAYER_BORED_THRESHOLD:
                        self.item_loc['p'][0].texture='sleeping'
                    self.item_loc['p'][0].idle_time+=1
                else:
                    self.item_loc['p'][0].texture='slight_smile'
                    self.item_loc['p'][0].idle_time=0
        
                        
                    
        

    def render(self, w, h):
        """
        Report status and list of sprite dictionaries for sprites with a
        horizontal distance of w//2 from player.  See writeup for details.
        """
        character_map={
            'B':'classical_building',
            'u':'cactus',
            'C':'castle',
            'c':'cloud',
            '=':'black_large_square',
            'p':'slight_smile',
            't':'tree'
        }
        player_loc=self.item_loc['p'][0].position
        visible=[]
        for object_type in self.item_loc:
            for item in self.item_loc[object_type]:
                item_rec=Rectangle(item.position[0],item.position[1],128,128)
                window_rec=Rectangle(player_loc[0]-w//2,-128,w,h+128)
                #if item_rec.intersects(window_rec):
                if item.position[0]>player_loc[0]-w//2-128 and item.position[0]<player_loc[0]+w//2 and item.position[1]>-128 and item.position[1]<h:
                    temp={
                        'texture': character_map[object_type],
                        'pos':item.position,
                        'player':False
                    }
                    if object_type=='p':
                        temp['player']=True
                        temp['texture']=item.texture
                    visible.append(temp)
        #print(player_loc)
        return (self.progress,visible)



if __name__ == "__main__":
    print(Rectangle.intersects([8,4,5,7],[3,4,5,7]))
    
    
