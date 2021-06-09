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

-- set addresses here
local DST_MAC           = nil -- resolved via ARP on GW_IP or DST_IP, can be overriden with a string here
local SRC_IP            = "192.168.0.7"
local DST_IP            = "192.168.0.9"
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
        parser:description("Generates UDP traffic and measure latencies. Edit the source to modify constants like IPs.")        parser:argument("txDev", "Device to transmit from."):convert(tonumber)
        parser:argument("txDev", "Device to transmit from."):convert(tonumber)
        parser:argument("rxDev", "Device to receive from."):convert(tonumber)
        parser:option("-r --rate", "Transmit rate in Mbit/s."):default(10000):convert(tonumber)
        parser:option("-s --size", "Packet size."):default(60):convert(tonumber)
        parser:option("-t --timeLimit", "Time limit in seconds."):default(10):convert(tonumber)
end

function master(args)
        txDev = device.config{port = args.txDev, rxQueues = 3, txQueues = 3}
        rxDev = device.config{port = args.rxDev, rxQueues = 3, txQueues = 3}
        device.waitForLinks()
        -- max 1kpps timestamping traffic timestamping
        -- rate will be somewhat off for high-latency links at low rates
        if args.rate > 0 then
                txDev:getTxQueue(0):setRate(args.rate - (args.size + 4) * 8 / 1000)
        end
        mg.startTask("loadSlave", txDev:getTxQueue(0), rxDev, args.size, args.timeLimit)
        -- mg.startTask("timerSlave", txDev:getTxQueue(1), rxDev:getRxQueue(1), args.size, args.flows)
        arp.startArpTask{
                -- run ARP on both ports 
                { rxQueue = rxDev:getRxQueue(2), txQueue = rxDev:getTxQueue(2), ips = RX_IP },
                -- we need an IP address to do ARP requests on this interface
                { rxQueue = txDev:getRxQueue(2), txQueue = txDev:getTxQueue(2), ips = ARP_IP }
        }
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
                pktLength = len
        }
end

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

function loadSlave(queue, rxDev, size, timeLimit)
        doArp()
        local mempool = memory.createMemPool(function(buf)
                fillUdpPacket(buf, size, queue)
        end)
        local bufs = mempool:bufArray()
        local counter = 0
        local txCtr = stats:newDevTxCounter(queue, "plain")
        local rxCtr = stats:newDevRxCounter(rxDev, "plain")
        local srcIP = parseIPAddress(SRC_IP)

        local runtime = nil
        if timeLimit then
                runtime = timer:new(timeLimit)
        end
        while mg.running() and (not runtime or runtime:running()) do
                bufs:alloc(size)
                for i, buf in ipairs(bufs) do
                        local pkt = buf:getUdpPacket()
                        pkt.ip4.src:set(srcIP)
                        pkt.payload.uint32[0] = counter
                        counter = counter + 1
                end
                -- UDP checksums are optional, so using just IPv4 checksums would be sufficient here
                bufs:offloadUdpChecksums()
                queue:send(bufs)
                txCtr:update()
                rxCtr:update()
        end
        txCtr:finalize()
        rxCtr:finalize()
end
