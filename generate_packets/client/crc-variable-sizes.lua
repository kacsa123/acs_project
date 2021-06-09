local dpdk   = require "dpdk"
local mg     = require "moongen"
local memory = require "memory"
local device = require "device"
local ts     = require "timestamping"
local filter = require "filter"
local hist   = require "histogram"
local stats  = require "stats"
local timer  = require "timer"
local arp    = require "proto.arp"
local log    = require "log"
local libmoon = require "libmoon"

-- set addresses here
local DST_MAC           = nil -- resolved via ARP on GW_IP or DST_IP, can be overriden with a string here 00:0f:53:44:64:d1
local SRC_IP            = "192.168.0.8"
local DST_IP            = "192.168.0.10"
local SRC_PORT          = 1234
local DST_PORT          = 5001

-- answer ARP requests for this IP on the rx port
-- change this if benchmarking something like a NAT device
local RX_IP             = SRC_IP
-- used to resolve DST_MAC
local GW_IP             = DST_IP
-- used as source IP to resolve GW_IP to DST_MAC
local ARP_IP            = SRC_IP

function configure(parser)
        parser:description("Generates UDP traffic and measure latencies. Edit the source to modify constants like IPs.")
        parser:argument("txDev", "Device to transmit from."):convert(tonumber)
        parser:option("-r --rate", "Transmit rate in M packets/s."):default(1):convert(tonumber)
        parser:option("-s --size", "Packet size."):default(60):convert(tonumber)
        parser:option("-t --timeLimit", "Time limit in seconds."):default(10):convert(tonumber)
        parser:option("-p --pattern", "Traffic pattern to use. cbr|poisson"):default("cbr")
end

function master(args)
        --txDev = device.config{port = args.txDev, rxQueues = 2, txQueues = 2}
        txDev = device.config{port = args.txDev, rxQueues = 2, txQueues = 2, disableOffloads = false}
        -- rxDev = device.config{port = args.rxDev, rxQueues = 3, txQueues = 3}
        device.waitForLinks()

        --if args.rate > 0 then
        --      txDev:getTxQueue(0):setRate(args.rate - (args.size + 4) * 8 / 1000)
        --end

        dpdk.launchLua(arp.arpTask, {
                { rxQueue = txDev:getRxQueue(1), txQueue = txDev:getTxQueue(1), ips = { "192.168.0.8" } }
        })
        --libmoon.sleepMillis(10000)
        mg.startTask("loadSlave", txDev:getTxQueue(0), args.size, args.rate, args.pattern, args.timeLimit)
        --arp.startArpTask{
                  -- run ARP on both ports
                -- { rxQueue = rxDev:getRxQueue(1), txQueue = rxDev:getTxQueue(1), ips = RX_IP },
                -- we need an IP address to do ARP requests on this interface
        --      { rxQueue = txDev:getRxQueue(1), txQueue = txDev:getTxQueue(1), ips = ARP_IP }
        --}
        mg.waitForTasks()
end

local function fillUdpPacket(buf, len, queue)
        buf:getUdpPacket():fill{
                ethSrc = queue,
                ethDst = DST_MAC,
                ip4Src = SRC_IP,
                ip4Dst = DST_IP,
                udpSrc = SRC_PORT,
                udpDst = DST_PORT,
                pktLength = 1500
        }
local function doArp()
        if not DST_MAC then
                log:info("Performing ARP lookup on %s", GW_IP)
                DST_MAC = arp.blockingLookup(GW_IP, 5)
                if not DST_MAC then
                        log:info("ARP lookup failed, using default destination mac address")
                        return
                end
        end
        log:info("Destination mac: %s", DST_MAC)
end

function loadSlave(queue, size, rate, pattern, timeLimit)
--function loadSlave(queue, rxDev, size, timeLimit)
        log:info("Start sending")
        doArp()
        local mempool = memory.createMemPool(function(buf)
                fillUdpPacket(buf, size, queue)
        end)
        local bufs = mempool:bufArray(128)
        local counter = 0
        local txCtr = stats:newDevTxCounter(queue, "plain")

        local srcIP = parseIPAddress(SRC_IP)

        local runtime = nil
        if timeLimit then
                runtime = timer:new(timeLimit)
        end
        local dist = pattern == "poisson" and poissonDelay or function(x) return x end

        while mg.running() and (not runtime or runtime:running()) do
                        bufs:alloc(1500)
                for i, buf in ipairs(bufs) do
                        local cur_size = math.max(dist(size), 60)
                        local pkt = buf:getUdpPacket()
                        pkt.ip4.src:set(srcIP)
                        pkt.payload.uint32[0] = counter
                        buf.pkt_len   = cur_size
                        buf.data_len  = cur_size
                        counter = counter + 1
                        buf:setDelay((10^4 / 8 / rate) - cur_size - 24)
                end
                -- UDP checksums are optional, so using just IPv4 checksums would be sufficient here
                bufs:offloadUdpChecksums()
                queue:sendWithDelay(bufs)
                txCtr:update()

        end
        txCtr:finalize()

end
