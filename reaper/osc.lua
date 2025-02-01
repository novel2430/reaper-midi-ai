-- Import Socket Module
local proj_name = 'test'
local extension = 'so'
local socket_path = reaper.GetResourcePath() .. "/Scripts/" .. proj_name .. "/luasocket/?." -- Change to your path here
package.cpath = package.cpath .. ";" .. socket_path .. extension  -- Add current folder/socket module for looking at .dll (need for loading basic luasocket)
package.path = package.path .. ";" .. socket_path .. "lua" -- Add current folder/socket module for looking at .lua ( Only need for loading the other functions packages lua osc.lua, url.lua etc... You can change those files path and update this line
local socket = require('socket.core')

-- Import Json Module
json = require('json')


-- Basic Setting
local host = "127.0.0.1"
local port = 12345

-- GUI Setting
local response_msg = "等待消息..."
local button_x, button_y, button_w, button_h = 50, 50, 200, 40
local window_w, window_h = 300, 150

-- TCP Client
local client = assert(socket.tcp())
client:connect(host, port)
client:settimeout(0) -- 非阻塞模式

local function get_midi_notes()
    local midi_notes = {}

    -- 获取当前选中的轨道
    local track = reaper.GetSelectedTrack(0, 0)
    if not track then return midi_notes end

    -- 获取轨道的 MIDI Item
    local item_count = reaper.CountTrackMediaItems(track)
    for i = 0, item_count - 1 do
        local item = reaper.GetTrackMediaItem(track, i)
        local take = reaper.GetTake(item, 0)
        if take and reaper.TakeIsMIDI(take) then
            local note_index = 0
            while true do
                local retval, _, _, _, _, _, pitch, _ = reaper.MIDI_GetNote(take, note_index)
                if not retval then break end
                table.insert(midi_notes, pitch)
                note_index = note_index + 1
            end
        end
    end

    return midi_notes
end

-- **发送 MIDI 数据**
local function send_midi()
    local midi_notes = get_midi_notes()
    if #midi_notes == 0 then
        response_msg = "没有找到 MIDI 音符"
        return
    end

    -- 转换为字符串并发送
    local message = table.concat(midi_notes, ",")
    client:send(message .. "\n")
    response_msg = "已发送: " .. message
end

-- **接收服务器消息**
local function receive_data()
    local response, err = client:receive()
    if response then
        response_msg = "服务器回复: " .. response
    elseif err ~= "timeout" then
        response_msg = "连接关闭或出错: " .. err
        return
    end

    -- 继续监听
    reaper.defer(receive_data)
end

-- **GUI 事件监听**
local function is_mouse_inside(x, y, w, h)
    local mx, my = gfx.mouse_x, gfx.mouse_y
    return mx >= x and mx <= x + w and my >= y and my <= y + h
end

-- **绘制 GUI**
local function draw_gui()
    gfx.init("MIDI 发送器", window_w, window_h)

    local function loop()
        if gfx.getchar() == -1 then
          -- Clean 
          client:close()
          return
        end
        gfx.clear = 0x303030 -- 背景色（灰色）

        -- 显示文本
        gfx.set(1, 1, 1, 1) -- 颜色 (白色)
        gfx.x, gfx.y = 20, 20
        gfx.drawstr(response_msg)

        -- 绘制按钮
        if is_mouse_inside(button_x, button_y, button_w, button_h) then
            gfx.set(0.7, 0.7, 0.7, 1) -- 鼠标悬浮时的颜色（浅灰）
        else
            gfx.set(0.5, 0.5, 0.5, 1) -- 默认颜色（深灰）
        end

        gfx.rect(button_x, button_y, button_w, button_h, true)

        -- 按钮文字
        gfx.set(1, 1, 1, 1) -- 颜色（白色）
        gfx.x, gfx.y = button_x + 60, button_y + 10
        gfx.drawstr("发送 MIDI")

        -- 监听鼠标点击
        if gfx.mouse_cap & 1 == 1 and is_mouse_inside(button_x, button_y, button_w, button_h) then
            send_midi()
        end

        -- 监听 ESC 退出窗口
        if gfx.getchar() == 27 then
            gfx.quit()
        end

        -- 持续刷新
        reaper.defer(loop)
    end

    loop()
end

reaper.atexit(function()
    client:close()
    gfx.quit()
end)

-- 启动 GUI 和接收循环

receive_data()

draw_gui()



