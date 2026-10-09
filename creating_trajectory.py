import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
import math

# Point заменил в коде на обычный словарь, так проще прототипировать
# class Point():
#     def __init__(self, x:float, y:float):
#         self.x = x
#         self.y = y
        
#     @property
#     def coordinate(self):
#         return (self.x, self.y)
#     @property
#     def x(self):
#         return self.x
#     @property
#     def y(self):
#         return self.y
    
#     @coordinate.setter
#     def coordinate(self, pair: tuple[float, float]):
#         if not isinstance(pair, (list, tuple)) or len(pair) != 2:
#           raise ValueError(
#               'Координаты должны быть кортежем или списком из двух чисел!'
#           )
#         self.x, self.y = pair
        
    # def __str__ (self):
    #     return(f"(x:{self.x}, y:{self.y})")
        
class RobotMap():
    full_path = {   
                    'x':    [],
                    'y':    [],
                    'yaw' : []
                }
    reversed_sliced_map = {   
                    'x':    [],
                    'y':    [],
                    'yaw' : []
                }
    
    path_to_log = ""
    
    def __init__(self, path_to_log):
        self.path_to_log = path_to_log
        self.rebuild_path_from_log(path_to_log)
    
    def rebuild_path_from_log(self, path_to_log):
        data = pd.read_csv(path_to_log)
        random_time = np.random.uniform(0.1, 1.5, len(data))
        growing_seconds = 0.0 + np.cumsum(random_time)

        data.insert(0, 'video_time', growing_seconds)
        
        x = data["robot_x"].values
        y = data["robot_y"].values
        yaw = data["robot_yaw_rad"].values
        self.full_path['x'] = x
        self.full_path['y'] = y
        self.full_path['yaw'] = yaw
        # print(data[['video_time', "timestamp", "robot_x", "robot_y", "robot_yaw_rad"]])

    def visualize_full_map(self):
        self.visualize_map(**self.full_path)
        
    def find_sliced_reverse_path(
        self, 
        start = -1,
        object_seen_at = 0, 
        step = -1
        ):
        ''' Поиск обрезанного пути по начальным и конечным координатам, где конец - момент с нахождением объекта, а начало - старт отсчёта.'''        
        if start != -1 and object_seen_at > start:
            raise "Невозможно составить последовательность: объект нельзя увидеть до начала сканирования (путь составлен от обратного значения координат)"
        if step == 0:
            raise "Невозможно составить последовательность: шаг не может быть равен нулю"
        
        actual_start = start if start != -1 else len(self.full_path['x']) - 1
        stop_index = object_seen_at + step 
        
        if stop_index < 0:
            self.reversed_sliced_map = {
                'x' : self.full_path['x'][actual_start :: step],
                'y' : self.full_path['y'][actual_start :: step],
                'yaw' : self.full_path['yaw'][actual_start :: step]
            }
        else:
            self.reversed_sliced_map = {
                'x' : self.full_path['x'][actual_start : stop_index : step],
                'y' : self.full_path['y'][actual_start : stop_index : step],
                'yaw' : self.full_path['yaw'][actual_start : stop_index : step]
            }
            
        # print(self.reverse_splitted_map)
    def visualize_sliced(self):
        self.visualize_map(**self.reversed_sliced_map)
        
    def visualize_map(self, x :list, y:list, yaw:list):
        # x = map['x']
        # y = map['y']
        # yaw = map['yaw']
        plt.figure(figsize=(8, 8))
        plt.plot(x, y, label="Trajectory", color="blue", zorder=1)
        plt.scatter(x[0], y[0], color="green", s=200, label="Start", zorder=3)
        plt.scatter(x[-1], y[-1], color="red", s=200, label="Finish", zorder=3)

        step = 268 # Выбрал случайное число, методом тыка (включает стрелки в карту)
        indices = np.arange(0, len(x), step)
        u = np.cos(yaw[indices])
        v = np.sin(yaw[indices])
        
        plt.quiver(x[indices], y[indices], u, v, color="darkorange", 
                   scale=10, width=0.005, label="Orientation (yaw)", zorder=2)        
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()
        plt.tight_layout()
        plt.show()
        
    def visualize_both(self):
        x_full   = self.full_path['x'] 
        y_full   = self.full_path['y'] 
        yaw_full = self.full_path['yaw']

        x_sliced = self.reversed_sliced_map['x'] 
        y_sliced = self.reversed_sliced_map['y'] 
        yaw_sliced = self.reversed_sliced_map['yaw']
        
        step_full = len(x_full) // 80
        indices_full = np.arange(0, len(x_full), step_full)
        u_forward = np.cos(yaw_full[indices_full])
        v_forward = np.sin(yaw_full[indices_full])
        
        step_sliced = len(x_sliced) // 20
        indices_sliced = np.arange(0, len(x_sliced), step_sliced)
        u_backward = np.cos(yaw_sliced[indices_sliced] - math.pi)
        v_backward = np.sin(yaw_sliced[indices_sliced] - math.pi/2) 
        
        fig, (ax_1, ax_2) = plt.subplots(1,2, figsize = (10,6))
        
        ax_1.plot(x_full, y_full, label="Trajectory", color="blue", zorder=1)
        ax_1.plot(x_sliced, y_sliced, label="Move_back_trajectory", color="orange", zorder=1)
        ax_1.scatter(x_full[0], y_full[0], color="green", s=200, label="Start", zorder=3)
        ax_1.scatter(x_full[-1], y_full[-1], color="red", s=200, label="Finish", zorder=3)
        ax_1.scatter(x_sliced[0], y_sliced[0], color="purple", s=50, label="Start_sliced", zorder=3)
        ax_1.scatter(x_sliced[-1], y_sliced[-1], color="pink", s=50, label="Finish_sliced", zorder=3)
        ax_1.quiver(x_full[indices_full], y_full[indices_full], u_forward, v_forward, color="darkblue", 
                   scale=10, width=0.005, label="Orientation (yaw)", zorder=2)
        ax_1.quiver(x_sliced[indices_sliced], y_sliced[indices_sliced], u_backward, v_backward, color="darkorange", 
                   scale=10, width=0.005, label="Sliced Orientation (yaw)", zorder=2)          
        ax_1.set_title('Вся траектория')
        ax_1.legend()
        
        ax_2.plot(x_sliced, y_sliced, label="Trajectory", color="orange", zorder=1)
        ax_2.scatter(x_sliced[0], y_sliced[0], color="purple", s=200, label="Start", zorder=3)
        ax_2.scatter(x_sliced[-1], y_sliced[-1], color="pink", s=200, label="Finish", zorder=3)
        ax_2.quiver(x_sliced[indices_sliced], y_sliced[indices_sliced], u_backward, v_backward, color="darkorange", 
                           scale=10, width=0.005, label="Sliced Orientation (yaw)", zorder=2)    
        ax_2.set_title('Траектория от конца до места с искомым объектом')
        ax_2.legend()
        
        plt.tight_layout()
        plt.show()
        
r = RobotMap("raw_data\\25_robot_and_participants.csv")
# r.visualize_full_map()
r.find_sliced_reverse_path(object_seen_at=2000)
r.visualize_both()

