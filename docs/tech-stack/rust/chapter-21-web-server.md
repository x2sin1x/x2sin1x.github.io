---
title: 项目：构建多线程 Web 服务器
weight: 210
---
# 第 21 章：项目——构建多线程 Web 服务器

> 本章目标：将 `TcpListener`、线程、通道、闭包和所有权组合起来，构建一个教学用的简单 HTTP 服务器与线程池。

## 构建单线程 Web 服务器

使用标准库监听本地端口，并读取客户端发来的 HTTP 请求。HTTP 请求由请求行、头部和空行组成；本项目只处理少量固定请求，不是生产服务器。

```rust
use std::{io::{Read, Write}, net::TcpListener};

fn main() -> std::io::Result<()> {
    let listener = TcpListener::bind("127.0.0.1:8080")?;
    for stream in listener.incoming() {
        let mut stream = stream?;
        let mut buffer = [0; 1024];
        let bytes_read = stream.read(&mut buffer)?;
        println!("{}", String::from_utf8_lossy(&buffer[..bytes_read]));
        stream.write_all(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")?;
    }
    Ok(())
}
```

浏览器访问 `http://127.0.0.1:8080/` 可观察响应。请求内容可能超过缓冲区，真实服务器还必须处理部分读写、请求解析和错误状态。

### 解析请求并生成响应

HTTP 请求的第一行包含方法、路径和协议版本。教学项目只识别固定请求行，并将根路径和 `/sleep` 映射到不同 HTML 文件：

```rust
use std::{
    fs,
    io::{Read, Write},
    net::TcpStream,
    thread,
    time::Duration,
};

fn handle_connection(mut stream: TcpStream) -> std::io::Result<()> {
    let mut buffer = [0; 1024];
    let bytes_read = stream.read(&mut buffer)?;
    let request = String::from_utf8_lossy(&buffer[..bytes_read]);
    let request_line = request.lines().next().unwrap_or("");

    let (status, filename) = match request_line {
        "GET / HTTP/1.1" => ("HTTP/1.1 200 OK", "hello.html"),
        "GET /sleep HTTP/1.1" => {
            thread::sleep(Duration::from_secs(5));
            ("HTTP/1.1 200 OK", "hello.html")
        }
        _ => ("HTTP/1.1 404 NOT FOUND", "404.html"),
    };

    let contents = fs::read_to_string(filename)?;
    let response = format!(
        "{status}\r\nContent-Length: {}\r\n\r\n{contents}",
        contents.len()
    );
    stream.write_all(response.as_bytes())
}
```

`read` 从 TCP 流读取字节，`write_all` 确保响应缓冲区全部写出。HTTP 头部和正文之间必须有空行；`Content-Length` 用字节数表示正文长度。示例只解析首行，并假设请求能一次读入缓冲区，足以说明 TCP 与 HTTP 的基本拼接过程。

### 准备页面并返回内容

在项目根目录创建 `hello.html` 和 `404.html`。服务器按当前工作目录读取文件，因此要从包含这两个文件的目录运行程序：

```html
<!-- hello.html -->
<html><body><h1>Hello!</h1><p>Hi from Rust</p></body></html>
```

```html
<!-- 404.html -->
<html><body><h1>404</h1><p>Not Found</p></body></html>
```

`handle_connection` 根据请求行选择文件，再将状态行、`Content-Length`、空行和正文写回连接。此时可分别访问 `/`、`/sleep` 和任意不存在的路径，观察成功响应、延迟响应与 404 响应。书中项目以此展示从单连接服务器逐步扩展的过程。

## 从单线程服务器改为多线程服务器

单线程服务器会顺序处理请求；一个慢请求会阻塞后续连接。使用固定数量的工作线程和任务队列可以并发处理请求，同时限制线程数量。

线程池由一组 worker 和共享接收队列组成。主线程接收连接并把处理闭包发送到队列；worker 阻塞等待任务并执行。核心类型可以先从任务和线程池接口开始：

```rust
use std::sync::{mpsc, Arc, Mutex};
use std::thread;

type Job = Box<dyn FnOnce() + Send + 'static>;

enum Message {
    NewJob(Job),
    Terminate,
}

pub struct ThreadPool {
    workers: Vec<Worker>,
    sender: mpsc::Sender<Message>,
}

impl ThreadPool {
    pub fn new(size: usize) -> Self {
        assert!(size > 0, "线程池至少需要一个 worker");
        let (sender, receiver) = mpsc::channel();
        let receiver = Arc::new(Mutex::new(receiver));
        let workers = (0..size)
            .map(|id| Worker::new(id, Arc::clone(&receiver)))
            .collect();
        Self { workers, sender }
    }

    pub fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        self.sender
            .send(Message::NewJob(Box::new(f)))
            .expect("所有 worker 已退出");
    }
}

impl Drop for ThreadPool {
    fn drop(&mut self) {
        for _ in &self.workers {
            self.sender.send(Message::Terminate).expect("无法通知 worker");
        }
        for worker in &mut self.workers {
            if let Some(thread) = worker.thread.take() {
                thread.join().expect("worker panic");
            }
        }
    }
}

struct Worker {
    thread: Option<thread::JoinHandle<()>>,
}

impl Worker {
    fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Message>>>) -> Self {
        let thread = thread::spawn(move || loop {
            let message = receiver.lock().expect("receiver poisoned").recv();
            match message {
                Ok(Message::NewJob(job)) => {
                    println!("worker {id} received a job");
                    job();
                }
                Ok(Message::Terminate) | Err(_) => {
                    println!("worker {id} stopping");
                    break;
                }
            }
        });
        Self { thread: Some(thread) }
    }
}
```

接收端由 `Arc<Mutex<_>>` 共享。worker 取到消息后释放锁，再执行任务，因此其他 worker 可继续领取工作。`Job` 是可跨线程移动、拥有 `'static` 生命周期的 `FnOnce` 闭包。线程池销毁时发送与 worker 数量相同的终止消息，再等待所有线程退出。

## 优雅关闭与清理

线程池应定义明确的关闭语义：通知 worker 停止接收任务，再 `join` 所有线程，保证资源有序清理。显式终止消息使 worker 能区分新任务和关闭命令。由于消息按队列顺序接收，已排队的任务会先于终止消息处理；`join` 等待正在运行的闭包完成。线程句柄放在 `Option<JoinHandle<()>>` 中，是因为 `join(self)` 会消耗句柄，而 `Drop::drop` 只能借用 `self`；调用 `take()` 后即可安全地取出并消费句柄。

最终服务器先创建固定大小的线程池，再把每个连接处理闭包交给它：

```rust
let pool = ThreadPool::new(4);

for stream in listener.incoming() {
    let stream = stream?;
    pool.execute(move || {
        if let Err(error) = handle_connection(stream) {
            eprintln!("处理连接失败：{error}");
        }
    });
}
```

HTTP 解析和响应构造仍由 `handle_connection` 等函数承担；线程池只负责调度任务。线程池关闭时应等待正在执行的任务完成，并让空闲 worker 退出。

在当前示例中，监听循环结束后 `ThreadPool` 离开作用域，`Drop` 会排队终止消息并等待 worker。正式服务还需要一个明确的停止信号来打断监听、停止接收新连接、完成或取消排队任务，再有序关闭线程池；仅实现线程池的 `Drop` 并不会自动为无限监听循环提供进程级的优雅关机机制。

## 小结与延伸

- `TcpListener` 接收连接，HTTP 响应由状态行、头部、空行和正文组成。
- 线程池将连接处理任务分发给固定 worker，兼顾并发处理和资源上限。
- 本项目用于学习所有权与并发组织；实际部署应使用经过审计、具备完整 HTTP 处理能力的服务器库。

完成本章后，可回到[教程首页](index.md)复习整条学习路线，并继续阅读 Rust 官方的 [Cargo Book](https://doc.rust-lang.org/stable/cargo/) 与 [Rust Reference](https://doc.rust-lang.org/stable/reference/)。

官方对应章节：[Final Project: Building a Multithreaded Web Server](https://doc.rust-lang.org/book/ch21-00-final-project-a-web-server.html)。
