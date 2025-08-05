#pragma once

#include <vector>
#include <string>
#include <optional>

#include "board.h"

std::vector<std::string> warn(Board& chesses, const std::string& color = "");

std::optional<std::string> dead(Board& chesses, const std::string& color);