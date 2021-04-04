const { Server } = require('net');

const server = new Server();

const options = {
    port: 8000,
    host: '0.0.0.0'
};

const END = 'END';

const users = new Map();

// FUNCTIONS //
function newUser(socket, name) {
    const randomColor = () => {
        const d = Math.random() > 0.5 ? '\x1b[1m' : '';
        const u = Math.round(Math.random()*5) + 31;
        return `${d}\x1b[${u}m`;
    }    
    const userName = randomColor() + name + '\x1b[0m';
    users.set(socket, userName);    
    alert(`Bienvenido ${userName}!`);
    return userName;
}

function write(socket, message) {    
    const maxSize = 65535-2;
    const msgSize = Buffer.byteLength(message, 'utf-8');
    const size = Math.min(msgSize, maxSize);

    const buffer = Buffer.alloc(size+2);
    buffer.writeUInt16LE(size);
    buffer.write(message, 2, "utf-8"); 

    socket.write(buffer);
}

function alert(message, socket) {
    for(let s of users.keys()) {
        if (s !== socket) {
            write(s, message);
        }        
    }
}

function chat(user, message, socket) {
    for(let s of users.keys()) {
        if (s !== socket) {
            write(s, `${user}: ${message}`);
        }        
    }
}

// EVENTS //
server.on('connection', socket => {
    //socket.setEncoding('utf-8');

    const remoteSocket = `${socket.remoteAddress}:${socket.remotePort}`;
    console.log(`New connection from ${remoteSocket}`);

    write(socket, 'Introduce tu nombre de usuario:');

    socket.on('data', buffer => {
        let message = buffer.toString('utf-8', 2);
        if (users.has(socket)) {
            if (message === END) {
                socket.end();
            } 
            else {                
                const user = users.get(socket);
                console.log(`${remoteSocket} -> ${user}: ${message}`);
                chat(user, message);
            }
        }
        else {
            const user = newUser(socket, message);
            console.log(`${remoteSocket} -> New user: ${user}`);
        }
    });

    socket.on('error', console.error);

    socket.on('close', hasError => {
        const user = users.get(socket);
        users.delete(socket);
        console.log(`${remoteSocket} -> ${user} disconnected`);
        alert(`${user} se desconectó!`, socket); 
    });
});

server.listen(options, () => {
    console.log(`Server is listening on port ${options.port}`);
});

// PROCESS HANDLING // 
process.stdin.resume();

async function exitHandler(options, exitCode = 0) {    
    if (options.exit) {
        for(let s of users.keys()) {
            await s.end();            
        }
        server.close(err => {
            console.log(err ? 1 : exitCode);
            process.exit(err ? 1 : exitCode);
        })
    }
}

process.on('exit', exitHandler.bind(null,{cleanup:true}));
process.on('SIGINT', exitHandler.bind(null, {exit:true}));
process.on('SIGUSR1', exitHandler.bind(null, {exit:true}));
process.on('SIGUSR2', exitHandler.bind(null, {exit:true}));
process.on('uncaughtException', exitHandler.bind(null, {exit:true}));