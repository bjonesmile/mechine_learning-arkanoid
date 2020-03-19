"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    last_ball_pos = (-1, -1)
    vector_n = (0, 0)

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        isDown = False
        isUp = False
        isRight = False
        isLeft = False
        move_R = False
        move_L = False
        if last_ball_pos[0] == -1 :
            last_ball_pos = scene_info.ball
        ball_pos = (scene_info.ball[0] + 2.5, scene_info.ball[1] + 2.5)
        platform_x = scene_info.platform[0]
        vector = 0
        if last_ball_pos[0] != -1 :
            vector = (ball_pos[1]-last_ball_pos[1])/(ball_pos[0]-last_ball_pos[0])
            if ball_pos[0]-last_ball_pos[0] > 0 :
                isRight = True
            elif ball_pos[0]-last_ball_pos[0] < 0 :
                isLeft = True
            else:
                pass
            
            if ball_pos[1]-last_ball_pos[1] < 0 :
                isUp = True
            elif ball_pos[1]-last_ball_pos[1] > 0 :
                isDown = True
            else:
                pass

        if isDown :
            predict_x = (400 - ball_pos[1])/vector + ball_pos[0]
            predict_y = 0
            if isRight:
                predict_y = (200 - ball_pos[0])*vector + ball_pos[1]
            elif isLeft:
                predict_y = (0 - ball_pos[0])*vector + ball_pos[1]

            if predict_x > 0 and predict_x < 200 :
                if predict_x > platform_x + 10 :
                    move_R = True
                elif predict_x < platform_x + 10:
                    move_L = True
                else :
                    pass
            elif isLeft and predict_y < 300 :
                if predict_x > 200 :
                    move_L = True
                    if platform_x < 50 :
                        move_L = False
                elif predict_x < 0 :
                    move_R = True
                    if platform_x +20 > 150 :
                        move_R = False
                else :
                    pass
            elif isLeft and predict_y > 300 and predict_y < 400:
                move_R = True
                if predict_x > -50 :
                    move_R = False

                if platform_x + 20 > 150 :
                    move_R = False
            elif isRight and predict_y < 300 :
                if predict_x > 200 :
                    move_L = True
                    if platform_x < 50 :
                        move_L = False
                elif predict_x < 0 :
                    move_R = True
                    if platform_x +20 > 150 :
                        move_R = False
                else :
                    pass
            elif isRight and predict_y > 300 and predict_y < 400 :
                move_L = True
                if predict_x < 350 :
                    move_L = False

                if platform_x < 50 :
                    move_L = False
            else :
                pass

        else :
            if platform_x + 10 > 100 :
                move_L = True
            elif platform_x + 10 < 100 :
                move_R = True
            else :
                pass

        vector = vector_n
        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:
            
            if move_R == True :
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            elif move_L == True :
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            else :
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            last_ball_pos = scene_info.ball
