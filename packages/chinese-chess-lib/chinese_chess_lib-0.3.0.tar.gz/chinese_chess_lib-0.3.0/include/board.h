#pragma once

#include <vector>
#include <string>
#include <utility>
#include <tuple>

using Pos = std::pair<int, int>;
using Move = std::tuple<bool, int, int>;  // (是否吃子, x偏移, y偏移)

struct Chess {
	int x, y;  // 棋子位置
	std::string name;
	std::string color;  // 棋子颜色，"#000000"为黑色，"#FF0000"为红色
};

using Board = std::vector<std::vector<Chess*>>;