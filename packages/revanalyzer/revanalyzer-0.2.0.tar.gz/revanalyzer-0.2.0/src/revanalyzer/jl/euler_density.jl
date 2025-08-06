using EulerCharacteristic
filename = ARGS[1]
dimz = parse(Int64, ARGS[2])
dimy = parse(Int64, ARGS[3])
dimx = parse(Int64, ARGS[4])
fpath = ARGS[5]
data = Array{UInt8, 3}(undef, dimx, dimy, dimz)
open(filename) do io read!(io, data) end
data = Bool.(data)
data = .!data
volume = dimx*dimy*dimz
density = euler_characteristic(data)/volume
print(density)
open(fpath, "w") do file
    write(file, string(density))
end
