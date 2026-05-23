import { promises as fs } from 'fs';
import http from 'isomorphic-git/http/node';
import git from 'isomorphic-git';

const dir = process.cwd();
const url = 'https://github.com/swanchou/sss.git';

async function main() {
    const token = process.argv[2];
    if (!token) {
        console.error('请提供 GitHub Personal Access Token');
        console.error('用法: node push-to-github.mjs <YOUR_TOKEN>');
        process.exit(1);
    }

    console.log('[1/5] 初始化 Git 仓库...');
    await git.init({ fs, dir });

    console.log('[2/5] 添加远程仓库...');
    try {
        await git.addRemote({ fs, dir, remote: 'origin', url, force: true });
    } catch (e) {
        // remote already exists, update it
    }

    console.log('[3/5] 添加所有文件...');
    await git.add({ fs, dir, filepath: '.' });

    console.log('[4/5] 创建提交...');
    await git.commit({
        fs,
        dir,
        message: '初始提交 - Excel识别工具',
        author: { name: 'swanchou', email: 'swanchou@users.noreply.github.com' }
    });

    console.log('[5/5] 推送到 GitHub...');
    await git.push({
        fs,
        dir,
        http,
        remote: 'origin',
        ref: 'main',
        onAuth: () => ({ username: token, password: 'x-oauth-basic' }),
    });

    console.log('');
    console.log('============================================');
    console.log('  推送成功！');
    console.log('  仓库地址: https://github.com/swanchou/sss');
    console.log('  请前往 GitHub → Actions 查看自动打包进度');
    console.log('============================================');
}

main().catch(err => {
    console.error('错误:', err.message);
    process.exit(1);
});