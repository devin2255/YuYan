from app import create_app

app = create_app()  # 生产环境: production(默认), 测试环境: test

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=18000)
