const { Socket } = require('net');
const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
});

const socket = new Socket();

const BYTES = 4;
const MAX_SIZE = Math.pow(2, BYTES*8) - 1;

socket.connect({host: 'localhost', port:8000});

const packet = {}

readline.on('line', message => {
    if (message !== 'exit') {
        const msgSize = Buffer.byteLength(message);        
        const size = Math.min(msgSize, MAX_SIZE);
    
        const buffer = Buffer.alloc(BYTES + size);
        buffer.writeUInt32LE(size);
        buffer.write(message, BYTES, "utf-8");         
    
        socket.write(buffer);
    }
    else {
        socket.end();
    }
})

socket.on('close', err => {
    if (err) {
        console.error(err);
        process.exit(1);
    }
    else {
        process.exit(0);
    }
});

socket.on('data', buffer => {
    if (packet.message) {
        packet.message += buffer.toString('utf-8');
    }
    else {
        packet.total = buffer.readUInt32LE();
        packet.message = buffer.toString('utf-8', BYTES);
    }

    if (packet.message.length === packet.total) {
        console.log(packet.message);
        delete packet.message;
    }
});

// PROCESS HANDLING // 
process.stdin.resume();

async function exitHandler(options, exitCode = 0) {    
    console.log(exitCode);
    if (options.exit) {
        socket.end();
    }
}

process.on('exit', exitHandler.bind(null,{cleanup:true}));
process.on('SIGINT', exitHandler.bind(null, {exit:true}));
process.on('SIGUSR1', exitHandler.bind(null, {exit:true}));
process.on('SIGUSR2', exitHandler.bind(null, {exit:true}));
process.on('uncaughtException', exitHandler.bind(null, {exit:true}));