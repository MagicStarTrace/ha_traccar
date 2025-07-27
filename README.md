# HA Traccar - Home Assistant Traccar 服务器集成




一个为 Home Assistant 提供的 Traccar 服务器集成，支持实时设备跟踪、传感器监控和事件响应。

> **注意**：本项目基于原版插件进行了改进，新增了 WGS84 坐标转换实体，特别适用于中国地区的地图服务。
> 
> **推荐环境**：建议配合 Docker 版本的 Traccar 使用，推荐镜像：`bg6rsh/traccar-amap:5.8`

## 功能特性

### 🚗 实时设备跟踪
- **GPS 定位跟踪**：实时更新设备位置信息
- **坐标系统支持**：支持 WGS84 和 GCJ02 坐标系统
- **智能坐标转换**：新增 WGS84 坐标实体，可直接用于家庭区域判断
- **位置准确性监控**：显示 GPS 定位精度
- **地址反向解析**：自动获取设备当前地址

### 📊 丰富的传感器支持
- **电池监控**：实时显示设备电池电量（百分比）
- **充电状态检测**：监控设备充电状态变化
- **运动检测**：检测设备是否在移动
- **网络状态**：显示设备在线/离线状态
- **速度监控**：实时显示设备移动速度（公里/小时）
- **海拔高度**：显示设备当前海拔（米）
- **行驶方向**：显示设备移动方向（度）
- **温度监控**：设备温度传感器（如果支持）
- **里程统计**：总行驶距离统计（公里）

### 🌍 地理围栏功能
- **围栏检测**：自动检测设备进入/离开地理围栏
- **多围栏支持**：支持多个地理围栏同时监控
- **围栏事件**：围栏进出事件触发

### ⚡ 实时事件系统
- **WebSocket 连接**：与 Traccar 服务器保持实时连接
- **即时更新**：设备状态变化立即推送到 Home Assistant
- **事件类型支持**：
  - 设备上线/离线
  - 开始/停止移动
  - 进入/离开地理围栏
  - 超速警告
  - 点火开关状态
  - 维护提醒
  - 报警事件

## 支持的实体类型

### 设备跟踪器 (Device Tracker)
每个 Traccar 设备会创建以下跟踪器实体：

| 实体ID | 名称 | 描述 |
|--------|------|------|
| `device_tracker.{设备名}_` | 标准设备跟踪器 | 显示设备在地图上的位置 |
| `device_tracker.{设备名}_wgs84` | WGS84坐标跟踪器 | **新增功能** - 提供转换后的精确坐标，可直接用于区域判断 |

**状态属性：**
- `latitude` / `longitude` - 设备坐标
- `gps_accuracy` - GPS 精度
- `address` - 当前地址
- `speed` - 移动速度
- `course` - 行驶方向
- `altitude` - 海拔高度
- `battery_level` - 电池电量
- `status` - 设备状态（在线/离线）
- `motion` - 运动状态
- `geofence` - 当前地理围栏

### 传感器 (Sensor)
每个设备会自动创建以下传感器：

| 实体ID | 名称 | 单位 | 设备类别 | 描述 |
|--------|------|------|----------|------|
| `sensor.{设备名}_battery` | 电池 | % | 电池 | 设备电池电量百分比 |
| `sensor.{设备名}_speed` | 速度 | km/h | 速度 | 设备移动速度 |
| `sensor.{设备名}_altitude` | 海拔 | m | 距离 | 设备当前海拔高度 |
| `sensor.{设备名}_course` | 方向 | ° | - | 设备行驶方向角度 |
| `sensor.{设备名}_address` | 地址 | - | - | 设备当前位置地址 |
| `sensor.{设备名}_geofence` | 地理围栏 | - | - | 当前所在地理围栏名称 |
| `sensor.{设备名}_temperature` | 温度 | °C | 温度 | 设备温度（如果支持） |
| `sensor.{设备名}_distance` | 距离 | km | 距离 | 总行驶距离 |

### 二进制传感器 (Binary Sensor)
每个设备会创建以下二进制传感器：

| 实体ID | 名称 | 设备类别 | 描述 |
|--------|------|----------|------|
| `binary_sensor.{设备名}_motion` | 运动 | 运动 | 设备是否在移动 |
| `binary_sensor.{设备名}_status` | 在线 | 连接性 | 设备在线状态 |
| `binary_sensor.{设备名}_charging` | 充电 | 电池充电 | 设备充电状态 |

## 安装方法

### 通过 HACS 安装（推荐）

1. 在 HACS 中添加自定义存储库：
   ```
   https://github.com/MagicStarTrace/ha_traccar
   ```

2. 搜索并安装 "HA Traccar"

3. 重启 Home Assistant

### 手动安装

1. 下载最新版本的源码
2. 将 `ha_traccar` 文件夹复制到 `custom_components` 目录
3. 重启 Home Assistant

## 配置方法

### 通过 UI 配置（推荐）

1. 进入 **配置** → **集成**
2. 点击 **添加集成**
3. 搜索 **Traccar 服务器**
4. 输入连接信息：
   - **主机名**：Traccar 服务器地址
   - **端口**：Traccar 服务器端口（默认 8082）
   - **用户名**：Traccar 账户用户名
   - **密码**：Traccar 账户密码
   - **SSL**：是否使用 HTTPS 连接
   - **SSL 验证**：是否验证 SSL 证书

### 高级配置选项

在集成配置页面的 **选项** 中可以设置：

#### 精度过滤
- **最大精度**：过滤精度低于指定值的位置数据（米）
- **跳过精度过滤的属性**：属性不受精度过滤影响


## 坐标系统支持

本集成支持多种坐标系统，特别针对中国地区：

### WGS84 坐标系（国际标准）
- **用途**：国际通用坐标系统
- **精度**：全球范围内精确
- **应用**：国外地图服务、GPS 设备原始数据

### GCJ02 坐标系（中国标准）
- **用途**：中国境内地图服务
- **精度**：在中国境内经过加密偏移
- **应用**：高德地图、腾讯地图等

### 坐标转换功能（新增特性）
- **智能坐标转换**：自动检测并转换坐标系统
- **双坐标支持**：在设备跟踪器属性中同时提供两种坐标
- **WGS84 专用实体**：新增独立的 WGS84 坐标跟踪器实体
- **区域判断优化**：WGS84 实体可直接用于 Home Assistant 的区域（Zone）判断
- **高精度转换**：配合 `bg6rsh/traccar-amap:5.8` 镜像获得最佳转换效果


## 故障排除

### 常见问题

#### 1. 设备无法连接
- 检查 Traccar 服务器地址和端口
- 确认用户名和密码正确
- 检查网络连接和防火墙设置

#### 2. 位置更新不及时
- 检查设备上报间隔设置
- 确认 WebSocket 连接正常
- 查看 Traccar 服务器日志

#### 3. 充电状态延迟
- 充电状态依赖位置数据更新
- 建议调整设备上报间隔或使用事件触发

#### 4. 坐标偏移问题
- 确认使用正确的坐标系统
- 检查坐标转换设置
- 验证设备GPS精度

### 日志调试

在 `configuration.yaml` 中添加调试日志：

```yaml
logger:
  default: warning
  logs:
    custom_components.ha_traccar: debug
    pytraccar: debug
```

### 支持的 Traccar 版本
- **Traccar 服务器**：4.0 及以上版本
- **Traccar 客户端**：所有版本
- **推荐 Docker 镜像**：`bg6rsh/traccar-amap:5.8`（已测试兼容）
- **推荐理由**：该镜像针对中国地区进行了优化，提供更好的地图服务和坐标转换支持

#### Docker 部署示例
```bash
docker run -d \
  --name traccar \
  -p 8082:8082 \
  -p 5013:5013 \
  -v /opt/traccar/data:/opt/traccar/data \
  bg6rsh/traccar-amap:5.8
```

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个集成。

### 开发环境设置
1. Fork 此项目
2. 创建开发分支
3. 进行修改并测试
4. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。


![截图](https://raw.githubusercontent.com/MagicStarTrace/ha_traccar/refs/heads/master/Add-Integration.jpg)
![截图](https://raw.githubusercontent.com/MagicStarTrace/ha_traccar/refs/heads/master/List-of-Entities.jpg)
![截图](https://raw.githubusercontent.com/MagicStarTrace/ha_traccar/refs/heads/master/New-entity-details.jpg)
![截图](https://raw.githubusercontent.com/MagicStarTrace/ha_traccar/refs/heads/master/Map.jpg)



---

如果此集成对您有帮助，请考虑给项目一个star ！ 
