function watchForChanges(db) {
    // 指定要监听的集合
    const collection = db.collection('yourCollectionName');
    
    // 创建Change Stream实例
    const changeStream = collection.watch();

    // 监听change stream事件
    changeStream.on('change', (change) => {
        console.log('Change detected:', change);

        // change对象包含变动详情，如：
        // - change.operationType: 变动类型（'insert', 'update', 'delete'等）
        // - change.fullDocument: 对于'insert'和'update'，包含完整文档
        // - change.documentKey: 发生变化的文档的_id
        // - change.updateDescription: 对于'update'，包含更新的字段详情

        // 根据operationType处理不同类型的变动
        switch (change.operationType) {
            case 'insert':
                console.log('Inserted document:', change.fullDocument);
                break;
            case 'update':
                console.log('Updated document:', change.updateDescription.updatedFields);
                break;
            case 'delete':
                console.log('Deleted document with _id:', change.documentKey._id);
                break;
            default:
                console.log('Other operation:', change.operationType);
        }
    });

    // 错误处理
    changeStream.on('error', (error) => {
        console.error('Error in change stream:', error);
    });
}
