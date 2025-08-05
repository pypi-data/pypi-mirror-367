#include <move.h>
#include <utility>
#include <stdexcept>
#include <optional>
#include <iostream>
#include <algorithm>

#include "rule.h"

std::vector<std::string> virtual_move(Board& chesses, Chess* chess, const Move& step, const std::string color) {
    int dx = std::get<1>(step);
    int dy = std::get<2>(step);

    // 移动前保存原状态
    Chess* temp = chesses[chess->y + dy][chess->x + dx];
    chesses[chess->y][chess->x] = nullptr;

    // 模拟移动
    chess->x += dx;
    chess->y += dy;
    chesses[chess->y][chess->x] = chess;

    // 调用回调函数
    std::vector<std::string> result = warn(chesses, color);

    // 回溯恢复状态
    chesses[chess->y][chess->x] = temp;
    chess->x -= dx;
    chess->y -= dy;
    chesses[chess->y][chess->x] = chess;

    return result;
}

std::vector<Move> get_legal_moves(Board& board, Chess* chess, bool flag_) {
    std::vector<Move> pos;

    auto ifappend = [&](const Move& step) -> bool {
        if (flag_) {
            std::string color = (chess->color == "#000000") ? "#FF0000" : "#000000";
            std::vector<std::string> result = virtual_move(board, chess, step, color);
            if (std::find(result.begin(), result.end(), color) != result.end()) {
                return false;
            }
        }
        return true;
        };

    auto append = [&](int dx, int dy, std::optional<bool> flag = std::nullopt) {
        if (flag.has_value() && flag.value()) {
            Move step = { true, dx, dy };
            if (ifappend(step)) pos.push_back(step);
        }
        else {
            int nx = chess->x + dx;
            int ny = chess->y + dy;
            Chess* target = board[ny][nx];
            if (target) {
                Move step = { true, dx, dy };
                if (target->color != chess->color && ifappend(step)) {
                    pos.push_back(step);
                }
            }
            else {
                Move step = { false, dx, dy };
                if (ifappend(step)) pos.push_back(step);
            }
        }
        };

    std::string name = chess->name;
    if (name == "j" || name == "J") {
        // 将帅走法：上下左右一步且在九宫格内
        static const std::vector<Pos> directions{ {1,0},{-1,0},{0,1},{0,-1} };
        for (auto [dx, dy] : directions) {
            int nx = chess->x + dx;
            int ny = chess->y + dy;
            if (nx >= 3 && nx <= 5 && ((ny >= 0 && ny <= 2) || (ny >= 7 && ny <= 9))) {
                append(dx, dy);
            }
        }
        // “见将”判定，直线检测对面将
        int startY = (chess->y <= 2) ? 1 : -1;
        for (int dy = startY; (dy > 0 ? chess->y + dy <= 9 : chess->y + dy >= 0); dy += startY) {
            int ny = chess->y + dy;
            if (ny < 0 || ny > 9) break;
            Chess* target = board[ny][chess->x];
            if (target) {
                if (target->name == "k" || target->name == "K") {
                    append(0, dy, true);
                }
                break;
            }
        }
    }
    else if (name == "s" || name == "S") {
        // 士走法：斜走一步，限制九宫格
        static const std::vector<Pos> directions{ {1,1},{-1,-1},{1,-1},{-1,1} };
        for (auto [dx, dy] : directions) {
            int nx = chess->x + dx;
            int ny = chess->y + dy;
            if (nx >= 3 && nx <= 5 && ((ny >= 0 && ny <= 2) || (ny >= 7 && ny <= 9))) {
                append(dx, dy);
            }
        }
    }
    else if (name == "x" || name == "X") {
        // 象走法：田字，不能过河，中间不能有子
        static const std::vector<Pos> directions{ {2,2},{-2,-2},{2,-2},{-2,2} };
        for (auto [dx, dy] : directions) {
            int nx = chess->x + dx;
            int ny = chess->y + dy;
            int mx = chess->x + dx / 2;
            int my = chess->y + dy / 2;
            if (nx >= 0 && nx <= 8 && (ny == 0 || ny == 2 || ny == 4 || ny == 5 || ny == 7 || ny == 9)) {
                if (!board[my][mx]) {
                    append(dx, dy);
                }
            }
        }
    }
    else if (name == "m" || name == "M") {
        // 马走法：日字，马腿不能被堵
        static const std::vector<Pos> directions{ {1,2},{1,-2},{-1,2},{-1,-2},{2,1},{-2,1},{2,-1},{-2,-1} };
        for (auto [dx, dy] : directions) {
            int nx = chess->x + dx;
            int ny = chess->y + dy;
            int legX = chess->x + (dx / abs(dx == 0 ? 1 : dx));
            int legY = chess->y + (dy / abs(dy == 0 ? 1 : dy));
            // 下面的马腿判断可根据实际规则调整
            int blockX = chess->x + (abs(dx) == 2 ? dx / 2 : 0);
            int blockY = chess->y + (abs(dy) == 2 ? dy / 2 : 0);
            if (nx >= 0 && nx <= 8 && ny >= 0 && ny <= 9) {
                if (!board[blockY][blockX]) {
                    append(dx, dy);
                }
            }
        }
    }
    else if (name == "c" || name == "C") {
        // 车走法：直线，遇阻停止，遇敌可吃
        for (int dir = 0; dir < 4; ++dir) {
            int dx = (dir == 1) ? -1 : (dir == 3) ? 1 : 0;
            int dy = (dir == 0) ? -1 : (dir == 2) ? 1 : 0;
            for (int step = 1; step <= 9; ++step) {
                int nx = chess->x + dx * step;
                int ny = chess->y + dy * step;
                if (nx < 0 || nx > 8 || ny < 0 || ny > 9) break;
                if (Chess* target = board[ny][nx]) {
                    if (target->color != chess->color) {
                        append(dx * step, dy * step, true);
                    }
                    break;
                }
                else {
                    append(dx * step, dy * step, false);
                }
            }
        }
    }
    else if (name == "p" || name == "P") {
        // 炮走法：直线，越一个子才能吃
        for (int dir = 0; dir < 4; ++dir) {
            int dx = (dir == 1) ? -1 : (dir == 3) ? 1 : 0;
            int dy = (dir == 0) ? -1 : (dir == 2) ? 1 : 0;
            bool jumped = false;
            for (int step = 1; step <= 9; ++step) {
                int nx = chess->x + dx * step;
                int ny = chess->y + dy * step;
                if (nx < 0 || nx > 8 || ny < 0 || ny > 9) break;
                if (Chess* target = board[ny][nx]) {
                    if (!jumped) {
                        jumped = true;
                    }
                    else {
                        if (target->color != chess->color) {
                            append(dx * step, dy * step, true);
                        }
                        break;
                    }
                }
                else {
                    if (!jumped) {
                        append(dx * step, dy * step, false);
                    }
                }
            }
        }
    }
    else if (name == "b" || name == "B") {
        // 兵卒走法，过河前只能直走，过河后能左右走
        bool isRed = (name == "B");
        int forward = isRed ? -1 : 1;

        int nx = chess->x;
        int ny = chess->y + forward;
        if (ny >= 0 && ny <= 9) {
            append(0, forward);
        }

        bool crossedRiver = isRed ? (chess->y <= 4) : (chess->y >= 5);
        if (crossedRiver) {
            for (int side : {-1, 1}) {
                nx = chess->x + side;
                if (nx >= 0 && nx <= 8) {
                    append(side, 0);
                }
            }
        }
    }
    else {
        throw std::invalid_argument("Invalid chess piece name" + name);
    }

    return pos;
}