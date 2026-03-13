-- Strips ANSI escape sequences from any block for GFM output

local function strip_ansi(s)
    return s:gsub("\27%[[0-9;]*[a-zA-Z]", "")
end

function Div(el)
    for _, b in ipairs(el.content) do
        if b.t == "RawBlock" or b.t == "CodeBlock" then
            b.text = strip_ansi(b.text)
        end
    end
    return el
end
