const { Socket } = require('net');
const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
});

const END = 'END';

const socket = new Socket();

socket.connect({host: 'localhost', port:8000});
//socket.setEncoding('utf-8');

readline.on('line', message => {
    const maxSize = 65535-2;
    const msgSize = Buffer.byteLength(message);
    const size = Math.min(msgSize, maxSize);

    const buffer = Buffer.alloc(size+2);
    buffer.writeUInt16LE(size);
    buffer.write(message, 2, "utf-8"); 

    socket.write(buffer);
    /*if (message === END) {
        socket.end();
    }*/
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
    console.log(buffer.toString('utf-8', 2));
});

// PROCESS HANDLING // 
process.stdin.resume();

async function exitHandler(options, exitCode = 0) {    
    if (options.exit) {
        socket.end();
    }
}

process.on('exit', exitHandler.bind(null,{cleanup:true}));
process.on('SIGINT', exitHandler.bind(null, {exit:true}));
process.on('SIGUSR1', exitHandler.bind(null, {exit:true}));
process.on('SIGUSR2', exitHandler.bind(null, {exit:true}));
process.on('uncaughtException', exitHandler.bind(null, {exit:true}));