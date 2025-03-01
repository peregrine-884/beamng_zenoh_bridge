from scipy.spatial.transform import Rotation as R
import math

# オイラー角（yaw, pitch, roll）を指定
yaw = 42  # Z軸回転（度単位）
pitch = 0 # Y軸回転（度単位）
roll = 0  # X軸回転（度単位）

# オイラー角をリストとして指定（yaw, pitch, rollの順）
euler_angles = [yaw, pitch, roll]

# scipyを使ってクォータニオンに変換（角度は度単位で指定可能）
rotation = R.from_euler('zyx', euler_angles, degrees=True)  # 'zyx'はyaw-pitch-rollの順序
quaternion = rotation.as_quat()  # クォータニオンを取得（[x, y, z, w]の順）

# 出力
print(f"({quaternion[0]:.1f}, {quaternion[1]:.1f}, {quaternion[2]:.8f}, {quaternion[3]:.8f})")
