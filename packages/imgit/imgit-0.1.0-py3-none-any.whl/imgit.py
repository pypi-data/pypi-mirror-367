import json
import os
import sys
import shutil
from urllib.parse import urlparse
import re
from git import Repo
import ruamel.yaml
import logging
import runcmd
import yaml
from time import sleep
from prettytable import PrettyTable, ALL
import pkg_resources  # part of setuptools
from progress.bar import Bar
import argparse

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

# 配置日志输出，使其在控制台显示
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def debugInfo(message):
    """
    一个简单的调试信息输出函数，使用Python的logging模块。
    :param message: 要输出的调试信息
    """
    logging.info(message)


# 创建参数解析器
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--detail', type=bool, help='detail')
parser.add_argument('-m', '--modules', type=list, help='modules')


class YHModuleDependency:
    name = ''
    count = 0
    native = 0
    deplist = []
    natvielist = []

    def __init__(self, name, count, native, deplist, natvielist):
        self.name = name
        self.count = count
        self.native = native
        self.deplist = deplist
        self.natvielist = natvielist


# yaml/json 数据模型
class YamlModuleModel:
    module = ''
    pod = ''
    version = ''
    git = ''
    branch = ''
    tag = ''
    path = ''
    new_tag = ''
    configurations = ''
    inhibit_warnings = False
    third = False
    source = ''

    def __init__(self, module, pod, version, git, branch, tag, path, newtag, configurations, inhibit_warnings, source):
        self.module = module
        self.pod = pod
        self.git = git
        self.branch = branch
        self.tag = tag
        self.path = path
        self.new_tag = newtag
        self.configurations = configurations
        self.inhibit_warnings = inhibit_warnings
        self.source = source


# 文件状态，如果result = 1 表示成功，result = 0 表示失败 -1 表示其他异常
class ModuleStatusModel:
    module = ''
    pod = ''
    result = 0
    pod = ''
    branch = ''
    msg = ''
    tag = ''
    git = ''
    third = False
    configurations = ''
    inhibit_warnings = False
    source = None

    def __init__(self, module, pod, res, branch, msg='', tag='', git='', configurations='', inhibit_warnings=False,
                 source=None):
        self.module = module
        self.result = res
        self.pod = pod
        self.msg = msg
        self.branch = branch
        self.tag = tag
        self.git = git
        self.configurations = configurations
        self.inhibit_warnings = inhibit_warnings
        self.source = source


# 读取json文件数据
def json_data(json_path):
    """
    :param json_path: json路径
    :return: 返回json数据
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"文件未找到: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data


# 写入文件
def update_yaml(yaml_path, data):
    """
    :param yaml_path: yaml路径
    :param data: yaml数据
    :return: 无返回值
    """
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml_parser = ruamel.yaml.YAML()
        yaml_parser.dump(data, f)


def save_dict_to_yaml(data, file_path):
    """
    保存字典到 YAML 文件
    :param data: 要保存的字典数据
    :param file_path: 文件路径
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)


# 加载yml/json文件
def load_data(data):
    """
    :param data: 读取的yaml或json数据
    :return: 返回转换之后的模型
    """
    convertDepList = []

    dependencies = data.get("dependencies", [])

    for cur_dep in dependencies:
        module = YamlModuleModel(module=cur_dep.get("module", None),
                                 pod=cur_dep["pod"],
                                 version=cur_dep.get("version", None),
                                 git=cur_dep.get("git", None),
                                 branch=cur_dep.get("branch", None),
                                 tag=cur_dep.get("tag", None),
                                 path=cur_dep.get("path", None),
                                 newtag=cur_dep.get("newtag", None),
                                 configurations=cur_dep.get("configurations", None),
                                 inhibit_warnings=cur_dep.get("inhibit_warnings", False),
                                 source=cur_dep.get("source", None)
                                 )
        convertDepList.append(module)

    return convertDepList


# 删除文件
def del_path(path):
    """
    :param path: 文件路径
    :return: 无返回值
    """
    os.remove(path)


# 清空文件夹及目录
def del_dir(path):
    """
    :param path: 文件路径
    :return: 无返回值
    """
    shutil.rmtree(path)


# 清空或者创建一个新的目录
def create_file(path):
    """
    情况或者创建一个目录
    :param path: 目录
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        del_dir(path)
        os.makedirs(path)


class RepoGit:
    """
    项目仓库管理
    """
    proj_path = ""
    repo = Repo

    def __init__(self, proj_path):
        """
        :param proj_path: 路径
        """
        self.proj_path = proj_path
        self.repo = Repo(path=proj_path, search_parent_directories=True)

    def most_recent_commit_message(self, branch):
        """
        当前分支最后一次的提交信息
        :return:
        """
        self.switch_branch(branch)
        commits = list(self.repo.iter_commits(branch, max_count=10))
        for commit in commits:
            message = commit.message
            if message and len(
                    message) > 0 and "Merge" not in message and "no message" not in message and "自动" not in message:
                return message, commit
        return "", ""

    def switch_branch(self, branch):
        """
        切换到新分支
        :param branch: 新分支名字
        :return:
        """
        try:
            self.repo.git.checkout(branch)
        except Exception:
            # 如果本地没有这个分支，从远程拉取并切换
            self.repo.git.checkout('-b', branch, f'origin/{branch}')

    # 获取所有的分支
    def get_branches(self):
        """
        :return: 返回分支列表
        """
        branch_list = self.repo.git.branch("-r")
        return branch_list

    # 获取当前分支
    def getCurrentBranch(self):
        """
        :return: 当前分支
        """
        return str(self.repo.active_branch)

    # 创建新分支
    def create_branch(self, branch):
        """
        :return: 新分支名
        """
        return self.repo.create_head(branch)

    # 推送分支到远端
    def push_branch(self, branch):
        """
        :return: 新分支名
        """
        self.repo.remotes.origin.push(refspec=branch)

    # 获取当前工作目录的文件状态，是否有改动
    # True 表示有改动未提交 False表示没有改动
    def is_dirty(self):
        return self.repo.is_dirty(index=True, working_tree=True, untracked_files=True)

    # 查看文件状态
    def status(self):
        return self.repo.git.status()

    @property
    def getStatusFormatStr(self):
        cmd = ["git", "status", "-s"]
        r = runcmd.run(cmd, cwd=self.proj_path)._raise()
        lines = r.out.splitlines()
        return "\n".join(lines)

    def _startswith(self, string):
        """return a list of files startswith string"""
        cmd = ["git", "status", "-s"]
        r = runcmd.run(cmd, cwd=self.proj_path)._raise()
        lines = r.out
        lines = []
        for line in r.out.splitlines():
            if line.find(string) == 0:
                lines.append(" ".join(line.split(" ")[2:]))
        return lines

    def untracked(self):
        """return a list of untracked files"""
        return self._startswith("??")

    # 提交代码
    def commit(self, msg):
        self.repo.git.commit(m=msg)

    def add(self, files):
        self.repo.git.add(all=True)


# 获取podspec对应的版本号
def get_version_for(pod_spec_path):
    """
    获取tag版本号
    :param pod_spec_path: podspec路径
    :param new_tag: 新的tag名字
    :return:
    """
    with open(pod_spec_path, 'r', encoding="utf-8") as f:
        for line in f:
            if "s.version" in line and "s.source" not in line:
                cur_tag = tag_with_version(line)
                return cur_tag
        f.close()
        return ""


# 重写podspec里对应的版本
def update_versionfor_podspec(pod_spec_path, new_tag):
    """
    重写podspec里对应的版本
    :param pod_spec_path: podspec路径
    :param new_tag: 新tag
    :return:
    """
    file_data = ""
    with open(pod_spec_path, 'r', encoding="utf-8") as f:
        for line in f:
            if "s.version" in line and "s.source" not in line:
                cur_tag = tag_with_version(line)
                line = line.replace(cur_tag, new_tag)
                print("修改tag " + cur_tag + " => " + new_tag)
            file_data += line
    with open(pod_spec_path, 'w', encoding="utf-8") as f:
        f.write(file_data)
        f.close()


# 获取字符串中的版本信息
def tag_with_version(version):
    """
    获取字符串中的版本信息
    :param version: 版本号
    :return:
    """
    p = re.compile(r'\d+\.(?:\d+\.)*\d+')
    vers = p.findall(version)
    ver = vers[0]
    return ver


# 根据tag自增生成新的tag
def incre_tag(tag):
    """
    tag最后一位自增
    :param tag: 原tag
    :return: 返回最后一位自增1后的tag
    """
    tags = tag.split(".")
    tag_len = len(tags)
    if tag_len > 1:
        endtag = tags[tag_len - 1]
        end_tag_num = int(endtag) + 1
        endtag = str(end_tag_num)
        tags[tag_len - 1] = endtag

    new_tag = ".".join(tags)
    return new_tag


def get_filename(url_str):
    """
    获取路径中的文件名
    :param url_str: 文件路径
    :return: 返回文件名
    """
    url = urlparse(url_str)
    i = len(url.path) - 1
    while i > 0:
        if url.path[i] == '/':
            break
        i = i - 1
    folder_name = url.path[i + 1:len(url.path)]
    if not folder_name.strip():
        return False
    if ".git" in folder_name:
        folder_name = folder_name.replace(".git", "")
    return folder_name


# 判断两个版本的大小，去除小数点，变为整数数组，依次比较大小1
# 2.2.3 = [2, 2, 3]
# 2.2.10 = [2, 2, 10]  2.2.10 > 2.2.3
# 相等返回0， v1 > v2 返回 1 v1 < v2 返回 -1
def compare_version(v1, v2):
    """
    比较两个tag， 判断两个版本的大小，去除小数点，变为整数数组，依次比较大小1
    :param v1: v1 tag入参
    :param v2:  v2 tag 入参
    :return: 相等返回0， v1 > v2 返回 1 v1 < v2 返回 -1
    """
    v1_list = v1.split(".")
    v2_list = v2.split(".")
    max_len = max(len(v1_list), len(v2_list))
    idx = 0
    while idx < max_len:
        c_v1 = 0
        c_v2 = 0
        if len(v1_list) > idx:
            c_v1 = int(v1_list[idx])
        if len(v2_list) > idx:
            c_v2 = int(v2_list[idx])
        if c_v2 > c_v1:
            return -1
        else:
            return 1
        idx += 1
    return 0


# 写入文件
def update_yaml(yaml_path, data):
    """
    :param yaml_path: yaml路径
    :param data: yaml数据
    :return: 无返回值
    """
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml_parser = ruamel.yaml.YAML()
        yaml_parser.dump(data, f)


# 更新podfileModule文件
def update_module_files(yaml_path, local_yaml_path, branch_result, n_branch, modules_name):
    """
    更新ymal文件，修改本地依赖和分支依赖
    :param yaml_path: PodfileModule路径
    :param local_yaml_path: PodfileLocal路径
    :param branch_result: 操作成功的模块列表
    :param n_branch: 新分支名
    :param modules_name: 模块仓库的父路径默认为modules
    :return:
    """
    # 获取ymal 数据
    podfile_module_data = json_data(yaml_path)
    dependenceList = []
    if "dependencies" in podfile_module_data:
        local_dependenceList = podfile_module_data["dependencies"]
        if local_dependenceList:
            dependenceList = local_dependenceList

    before_branch = ''
    if "branch" in podfile_module_data:
        before_branch = podfile_module_data['branch']
    # 转换成模型数组
    conver_deplist = load_data(podfile_module_data)

    index = 0
    for a in conver_deplist:
        for mo_re in branch_result:
            if a.module and mo_re.module and a.module == mo_re.module and mo_re.result == 1:
                module_dict = {"module": mo_re.module, "pod": a.pod, "git": a.git, "branch": n_branch,
                               "configurations": a.configurations,
                               "inhibit_warnings": a.inhibit_warnings}
                dependenceList[index] = module_dict
        index += 1
    except_list = [
        module for module in branch_result if ((module.result == 1) and (module.module not in [
            pod.module for pod in conver_deplist]))]
    if len(except_list) > 0:
        for mo_re in except_list:
            module_dict = {
                "module": mo_re.module,
                "pod": mo_re.pod,
                "git": mo_re.git,
                "branch": n_branch
            }
            dependenceList.append(module_dict)

    if not (before_branch and len(before_branch) > 0):
        before_branch = n_branch
    podfile_data = {"version": "1.0.0", "branch": str(before_branch), "dependencies": dependenceList}
    save_dict_to_yaml(podfile_data, yaml_path)

    after_convert = []
    if not os.path.exists(local_yaml_path):
        shutil.copy(yaml_path, local_yaml_path)  # 复制文件
        for mo_re in branch_result:
            if mo_re.result == 1:
                module_dict = {"module": mo_re.module, "pod": mo_re.module, "path": modules_name + "/" + mo_re.module}
                after_convert.append(module_dict)
        local_module_data = {"version": "1.0.0", "branch": str(n_branch), "dependencies": after_convert}
        save_dict_to_yaml(local_module_data, local_yaml_path)

    else:
        local_module_data = json_data(local_yaml_path)
        local_dependenceList = []
        conver_deplist = []
        if local_module_data:
            if "dependencies" in local_module_data:
                local_dependenceList = local_module_data["dependencies"]
            if not local_dependenceList:
                local_dependenceList = []
            conver_deplist = load_data(local_module_data)
        except_list = [
            module for module in branch_result if ((module.result == 1) and (module.module not in [
                pod.module for pod in conver_deplist]))]
        if len(except_list) > 0:
            for mo_re in except_list:
                module_dict = {"module": mo_re.module, "pod": mo_re.pod, "path": modules_name + "/" + mo_re.module}
                local_dependenceList.append(module_dict)

        local_module_data = {"version": "1.0.0", "branch": str(n_branch), "dependencies": local_dependenceList}
        save_dict_to_yaml(local_module_data, local_yaml_path)


# 更新podfileModule文件
def merge_for_module_files(yaml_path, branch_result, n_branch):
    """
    更新ymal文件，修改本地依赖和分支依赖
    :param yaml_path: PodfileModule路径
    :param branch_result: 操作成功的模块列表
    :param n_branch: 新分支名
    :return:
    """
    # 获取ymal 数据
    podfile_module_data = yaml_data(yaml_path)
    dependenceList = podfile_module_data["dependencies"]
    # 转换成模型数组
    conver_deplist = load_yaml(dependenceList)

    index = 0
    for a in conver_deplist:
        for mo_re in branch_result:
            if a.module and mo_re.module and a.module == mo_re.module and mo_re.result == 1:
                module_dict = {"module": a.module, "pod": a.pod, "git": a.git, "tag": mo_re.tag,
                               "configurations": a.configurations,
                               "inhibit_warnings": a.inhibit_warnings}
                dependenceList[index] = module_dict
        index += 1
    podfile_data = {"version": "1.0.0", "branch": n_branch, "dependencies": dependenceList}
    update_yaml(yaml_path, podfile_data)


# 自动打tag 自动合并失败时返回空字符串
# 1. 清空当前工作目录
# 2. 拉取代码
# 3. 修改s.version
# 4. 提交代码
# 5. 拉取工作分支
# 5. 推送代码
def auto_release_path(filepath, git, pod, branch, new_tag):
    """
    自动合并branch到master中，并提交tag
    :param filepath: 文件路径
    :param git: git地址
    :param pod: pod模块
    :param branch: 分支
    :param new_tag: 新tag
    :return:
    """
    create_file(filepath)

    # return
    # 进入模块
    # clone 代码
    git_clone_command = "git clone -b master" + " " + git + " " + filepath
    # git add 代码
    git_add_command = "git add -A"
    # git pull branch 代码
    git_pull_command = "git pull origin " + branch

    # git push
    git_push_command = "git push origin master"
    # 用newTag来修改podspec中version
    os.system(git_clone_command)
    # print("执行 " + git_clone_command)
    # master分支下的版本号

    # 获取开发分支最后一次提交的信息
    repogit = RepoGit(proj_path=filepath)
    commit_message, commit = repogit.most_recent_commit_message(branch)
    repogit.switch_branch('master')
    git_commit_command = "git commit -m \'自动提交，修改tag\'"
    os.chdir(filepath)
    cur_tag = get_version_for(pod + ".podspec")
    os.system("pwd")
    os.system("ls")
    os.system(git_add_command)
    # print("执行 " + git_add_command)
    os.system(git_commit_command)
    # print("执行 " + git_commit_command)
    pul_status = os.system(git_pull_command)
    # print("执行 " + git_pull_command)
    if not pul_status == 0:
        debugInfo("代码冲突了")
        return ""
    dev_branch_tag = get_version_for(pod + ".podspec")
    new_tag_p = dev_branch_tag
    if dev_branch_tag == cur_tag:
        # 版本号一样就最后一位自增
        new_tag_p = incre_tag(cur_tag)
    else:
        # 版本号不一样，就比较如果开发分支比较大就用开发分支，否则还是自增
        res = compare_version(dev_branch_tag, cur_tag)
        if res == -1:
            new_tag_p = incre_tag(cur_tag)

    update_versionfor_podspec(pod + ".podspec", new_tag_p)
    os.system(git_add_command)
    # print("执行 " + git_add_command)
    os.system(git_commit_command)
    # print("执行 " + git_commit_command)
    # print("代码已经提交到master")
    # git pull branch 代码

    full_tag_message = '自动Tag 分支: {0} '.format(branch)
    if commit_message and len(commit_message) > 0:
        full_tag_message = full_tag_message + "最后提交信息： \"{0}\"   提交号：{1}".format(commit_message, commit.hexsha)
    git_tag_command = "git tag -a {0} -m \'{1}\'".format(new_tag_p, full_tag_message)
    # os.system(git_tag_command)
    # git_push_tag_command = "git push origin {0} ".format(new_tag_p)
    os.system(git_push_command)
    # print("执行 " + git_push_command)
    return new_tag_p


# 基于podfileModule来给每个组件创建一个分支
def create_branch(module_list, module_f_path, n_branch, modules, c_path):
    """
    基于列表，拉取对应代码，并创建一个开发分支
    :param module_list: 模块列表
    :param module_f_path: 路径
    :param n_branch: 新分支
    :param modules: 这些模块新建n_branch分支
    :param c_path: 当前的工作目录
    :return:
    """
    create_branch_result = []
    bar = Bar('install...', fill="*", max=len(modules))
    for a in module_list:
        if a.module in modules:
            bar.next()
            if not (a.branch and len(str(a.branch)) > 0):
                a.branch = "master"
            if (a.branch and len(str(a.branch)) > 0) or (a.tag and len(str(a.tag)) > 0):
                filename = a.module
                module_path = module_f_path + filename + "/"
                error_info = ''
                if not os.path.exists(module_path):
                    git_url = a.git
                    if not (a.git and len(a.git) > 0):
                        git_url = "http://gitlab.yonghui.cn/operation-xm-qdjg/{0}-snapshot.git".format(a.module.lower)
                    branch_name = auto_create_branch(module_path, git_url, a.branch, a.tag, n_branch)
                else:
                    local_branch = RepoGit(proj_path=module_path).getCurrentBranch()
                    error_info = "本地有工作目录: {0}，当前分支是：{1}".format(a.pod, local_branch)
                    branch_name = ''
                res = 1
                if not (branch_name and len(branch_name) > 0):
                    res = 0
                new_branch_model = ModuleStatusModel(a.module, a.pod, res, n_branch, error_info,
                                                     inhibit_warnings=a.inhibit_warnings,
                                                     configurations=a.configurations, source=a.source)
                create_branch_result.append(new_branch_model)
            else:
                new_branch_model = ModuleStatusModel(a.module, a.pod, 0, n_branch,
                                                     "podfileModule.yaml 中组件: " + a.pod + " 的branch或者tag为空, 不能确定要拉取的代码的位置",
                                                     inhibit_warnings=a.inhibit_warnings,
                                                     configurations=a.configurations, source=a.source)
                create_branch_result.append(new_branch_model)
    os.chdir(c_path)
    bar.finish()
    return create_branch_result


# 基于master 和 f_tag，创建一个新的分支new_branch，如果存在仓库则先清空仓库，再拉取分支
# 1. 清空当前工作目录
# 2. 拉取代码
# 3. 新建分支
# 4. 推送分支
def auto_create_branch(filepath, git, f_branch, f_tag, n_branch):
    """
    :param filepath: 文件路径
    :param git: git地址
    :param f_branch: 基于哪个分支切一个新的开发分支
    :param f_tag: 基于哪个tag切开发分支
    :param n_branch: 新分支名
    :return: 成功返回新分支名，失败返回空字符串
    """
    # 创建分支
    create_file(filepath)
    return new_branch(filepath, git, f_branch, f_tag, n_branch)


# 新建分支
def new_branch(filepath, git, f_branch, f_tag, n_branch):
    """
    f_branch 和 f_tag，创建一个新的分支n_branch
    2. 拉取代码
    3. 判断是否存在新分支，有新分支直接切到新分支
    3. 新建分支
    4. 切换到新分支
    4. 推送分支
    :param filepath: 路径
    :param git: git地址
    :param f_branch: 基于哪个分支切一个新的开发分支
    :param f_tag:  基于哪个tag切开发分支
    :param n_branch: 新分支名
    :return: 成功返回新分支名，失败返回空字符串
    """
    origin_branch = f_branch
    if not (f_branch and len(f_branch) > 0):
        origin_branch = "master"
    if f_branch and len(f_branch) > 0 and f_branch == n_branch:
        origin_branch = "master"
    # clone 代码
    git_clone_command = "git clone -b " + origin_branch + " " + git + " " + filepath
    # 创建一个新分支
    git_create_branch = "git branch " + n_branch
    if f_tag and len(f_tag) > 0:
        git_create_branch += " " + f_tag
    create_status = 0
    create_status += os.system(git_clone_command)
    # master分支下的版本号
    repoGit = RepoGit(proj_path=filepath)
    branchs = repoGit.get_branches()
    # debugInfo(str(branchs))
    os.chdir(filepath)
    if n_branch in branchs:
        debugInfo(n_branch + "分支已存在")
        repoGit.repo.git.execute(['git', 'checkout', n_branch])
        return n_branch
    try:
        # 创建并切换到新分支
        new_b = repoGit.create_branch(n_branch)
        new_b.checkout()
        # 推送新分支到远程仓库
        repoGit.push_branch(new_b)
    except Exception as e:
        print(str(e))
        debugInfo("新分支创建失败")
        return ""
    debugInfo("新分支创建成功")
    return n_branch


# 基于PodfileLocal，提交所有模块开发分支代码
def commit_branch(module_list, include_list, module_f_path, msg):
    """
    基于列表，提交对应开发分支代码
    :param module_list: 模块列表
    :param module_f_path: 路径
    :param msg: 提交信息
    :return: 返回操作的分支
    """
    commit_result = []
    invert_list = module_list
    if len(include_list) > 0:
        invert_list = [i for i in module_list if i.module in include_list]
    for i, module in enumerate(invert_list):
        path = module.path
        if not (path is not None and os.path.exists(path)):
            path = module_f_path + module.module + "/"
        module.path = path
    bar = Bar('commit...', fill="*", max=len(invert_list))
    for module in invert_list:
        bar.next()
        module_path = module.path
        result = 1
        branch = ''
        error_msg = ''
        if not os.path.exists(module_path):
            result = 0
            error_msg = "本地开发路径为空"
        else:
            git = None
            try:
                git = RepoGit(module_path)
            except Exception as e:
                result = 0
                error_msg = str(e)
            finally:
                if result != 0:
                    branch = git.getCurrentBranch()
                    error_msg = ''
                    result = 0
                    if not git.is_dirty():
                        error_msg = "很干净，没有可提交的"
                    else:
                        # 判断是否有没有追踪的文件
                        untracks = git.untracked()
                        git.add(untracks)
                        git.commit(msg)
                        result = not git.is_dirty()
                        if result == 0:
                            error_msg = "提交失败"
        modul_branch_model = ModuleStatusModel(module.module, module.pod, result, branch, error_msg)
        commit_result.append(modul_branch_model)
    bar.finish()
    return commit_result


# 基于podfileModule，提交模块开发分支代码
def pull_branch(module_list, include_list, module_f_path):
    """
    基于列表，提交对应开发分支代码
    :param module_list: 模块列表
    :param module_f_path: 路径
    :return: 返回操作的分支
    """
    invert_list = module_list;
    if len(include_list) > 0:
        invert_list = [i for i in module_list if i.module in include_list]

    for i, module in enumerate(invert_list):
        path = module.path
        if not (path is not None and os.path.exists(path)):
            path = module_f_path + module.module + "/"
        module.path = path

    pull_result = []
    bar = Bar('pull...', fill="*", max=len(invert_list))
    for module in invert_list:
        bar.next()
        msg = ''
        result = 1
        module_path = module.path
        branch = ''
        if not os.path.exists(module_path):
            result = 0
            msg = "本地开发路径为空"
        else:
            git = RepoGit(module_path)
            branch = git.getCurrentBranch()
            if git.is_dirty():
                result = -1
                msg = "本地有变动未提交，请确认"
            else:
                # ori = git.repo.remotes.origin
                try:
                    git.repo.git.pull('--progress', '--no-rebase', 'origin', branch)
                except Exception as e:
                    result = 0
                    msg = str(e)

        modul_branch_model = ModuleStatusModel(module.module, module.pod, result, branch, msg)
        pull_result.append(modul_branch_model)
    bar.finish()
    return pull_result


# 基于podfileModule，提交模块开发分支代码
def push_branch(module_list, include_list, module_f_path):
    """
    基于列表，提交对应开发分支代码
    :param module_list: 模块列表
    :param module_f_path: 路径
    :return: 返回操作的分支
    """

    index = 0
    pull_result = []
    invert_list = module_list;
    if len(include_list) > 0:
        invert_list = [i for i in module_list if i.module in include_list]

    for i, module in enumerate(invert_list):
        path = module.path
        if not (path is not None and os.path.exists(path)):
            path = module_f_path + module.module + "/"
        module.path = path

    bar = Bar('push...', fill="*", max=len(invert_list))
    for module in invert_list:
        bar.next()
        module_path = module.path
        msg = ''
        result = 1
        branch = ''
        if not os.path.exists(module_path):
            result = 0
            msg = "本地开发路径为空"
        else:
            git = RepoGit(module_path)
            branch = git.getCurrentBranch()

            if git.is_dirty():
                result = -1
                msg = "本地有变动未提交，请确认"
            else:
                try:
                    git.repo.git.pull('--progress', '--no-rebase', 'origin', branch)
                    git.repo.git.push('--progress', 'origin', branch)
                except Exception as e:
                    result = 0
                    msg = str(e)

        modul_branch_model = ModuleStatusModel(module.module, module.pod, result, branch, msg)
        pull_result.append(modul_branch_model)
    bar.finish()
    return pull_result


# 合并from_branch中代码到当前的开发分支
def merge_branch(module_list, convert_list, module_f_path, from_branch):
    """
    基于列表，提交对应开发分支代码
    :param module_list: 模块列表
    :param convert_list: 模块列表
    :param module_f_path: 路径
    :param from_branch: 要合并的分支
    :return: 返回操作的分支
    """
    index = 0
    pull_result = []
    invert_list = convert_list
    if len(module_list) > 0:
        invert_list = [i for i in convert_list if i.module in module_list]

    for i, module in enumerate(invert_list):
        path = module.path
        if not (path is not None and os.path.exists(path)):
            path = module_f_path + module.module + "/"
        module.path = path

    bar = Bar('merge...', fill="*", max=len(invert_list))
    for module in invert_list:
        if module.module in module_list:
            bar.next()
            module_path = module.path
            msg = ''
            result = 1
            branch = ''
            if not os.path.exists(module_path):
                result = 0
                msg = "本地开发路径为空"
            else:
                git = RepoGit(module_path)
                branch = git.getCurrentBranch()
                if git.is_dirty():
                    result = -1
                    msg = "本地有变动未提交，请确认"
                else:
                    branchs = git.get_branches()
                    if from_branch not in branchs:
                        result = -1
                        msg = "分支： {0} 不存在".format(from_branch)
                    else:
                        try:
                            if 'origin/' not in from_branch:
                                from_branch = "origin/" + from_branch
                            git.repo.git.pull('--progress', '--no-rebase', 'origin', branch)
                            git.repo.git.merge(from_branch)
                            git.repo.git.push('--progress', 'origin', branch)
                        except Exception as e:
                            result = 0
                            msg = str(e)
            modul_branch_model = ModuleStatusModel(module.module, module.pod, result, branch, msg)
            pull_result.append(modul_branch_model)
        index += 1
    bar.finish()
    return pull_result


# 合并from_branch中代码到当前的开发分支
def rebase_branch(module_list, convert_list, module_f_path, from_branch):
    """
    基于列表，提交对应开发分支代码
    :param module_list: 模块列表
    :param convert_list: 模块列表
    :param module_f_path: 路径
    :param from_branch: 要合并的分支
    :return: 返回操作的分支
    """
    index = 0
    pull_result = []
    if len(module_list) > 0:
        invert_list = [i for i in convert_list if i.module in module_list]

    for i, module in enumerate(invert_list):
        path = module.path
        if not (path is not None and os.path.exists(path)):
            path = module_f_path + module.module + "/"
        module.path = path

    bar = Bar('rebase...', fill="*", max=len(invert_list))
    for module in invert_list:
        if module.module in module_list:
            bar.next()
            module_path = module.path
            msg = ''
            result = 1
            if not os.path.exists(module_path):
                result = 0
                msg = "本地开发路径为空"
            else:
                git = RepoGit(module_path)
                branch = git.getCurrentBranch()
                msg = ''
                result = 1
                if git.is_dirty():
                    result = -1
                    msg = "本地有变动未提交，请确认"
                else:
                    branchs = git.get_branches()
                    if from_branch not in branchs:
                        result = -1
                        msg = "分支： {0} 不存在".format(from_branch)
                    else:
                        try:
                            git.repo.git.merge(from_branch)
                            git.repo.git.push('--progress', 'origin', branch)
                        except Exception as e:
                            result = 0
                            msg = str(e)
            modul_branch_model = ModuleStatusModel(module.module, module.pod, result, branch, msg)
            pull_result.append(modul_branch_model)
        index += 1
    bar.finish()
    return pull_result


# 基于podfileModule，提交模块开发分支代码
def release_branch(module_list, include_list, tag_path, c_path, f_branch):
    """
    基于模块列表，合并对应开发分支代码到master并打新的tag
    :param module_list: 模块列表
    :param include_list: 包含的模块名列表
    :param tag_path: 模块仓库的父路径
    :param c_path: 当前的工作目录
    :param f_branch: 需合并到master的分支
    :return: 返回操作的分支结果列表
    """
    release_result = []
    invert_list = module_list
    if len(include_list) > 0:
        invert_list = [i for i in module_list if i.module in include_list]

    for i, module in enumerate(invert_list):
        path = module.path
        if not (path is not None and os.path.exists(path)):
            path = tag_path + module.module + "/"
        module.path = path

    bar = Bar('releasing...', fill="*", max=len(invert_list))
    for module in invert_list:
        bar.next()
        module_path = module.path
        msg = ''
        result = 1
        tag = ''
        branch = ''

        if not os.path.exists(module_path):
            result = 0
            msg = "本地开发路径为空"
        else:
            try:
                git = RepoGit(module_path)
                branch = git.getCurrentBranch()
                if git.is_dirty():
                    result = -1
                    msg = "本地有变动未提交，请确认"
                else:
                    # 切换到 master 分支
                    git.switch_branch('master')
                    # 拉取最新代码
                    git.repo.git.pull('--progress', 'origin', 'master')
                    # 合并开发分支
                    git.repo.git.merge(f_branch)
                    # 推送合并后的 master 分支
                    git.repo.git.push('--progress', 'origin', 'master')

                    # 自动生成新的 tag
                    podspec_file = module_path + module.pod + ".podspec"
                    current_tag = get_version_for(podspec_file)
                    new_tag = incre_tag(current_tag)

                    # 更新 podspec 文件中的版本
                    update_versionfor_podspec(podspec_file, new_tag)

                    # 提交版本号修改
                    git.add([])  # 确保提交所有更改
                    git.commit(f"Update version to {new_tag}")
                    git.repo.git.push('--progress', 'origin', 'master')

                    # 创建并推送 tag
                    git.repo.git.tag('-a', new_tag, m=f"Release from branch {f_branch}")
                    git.repo.git.push('--progress', 'origin', new_tag)

                    tag = new_tag
                    msg = "发布成功，新tag: " + new_tag

            except Exception as e:
                result = 0
                msg = str(e)
            finally:
                # 无论成功失败，都切换回原开发分支
                if branch and len(branch) > 0:
                    git.switch_branch(branch)

        modul_branch_model = ModuleStatusModel(module.module, module.pod, result, branch, msg, tag)
        release_result.append(modul_branch_model)

    bar.finish()
    os.chdir(c_path)  # 切换回原始工作目录
    return release_result


def debugInfo(message):
    """
    一个简单的调试信息输出函数，使用Python的logging模块。
    :param message: 要输出的调试信息
    """
    logging.info(message)


def main():
    """
    主函数，用于解析命令行参数并执行相应操作。
    """
    parser = argparse.ArgumentParser(description='Automate Git repository management for modules.')
    parser.add_argument('-d', '--detail', action='store_true', help='Show detailed results of operations.')
    parser.add_argument('-m', '--modules', nargs='+', default=[], help='List of modules to operate on.')
    parser.add_argument('-b', '--branch', type=str, help='The branch name to create, merge from, or push to.')
    parser.add_argument('-c', '--command', type=str, required=True,
                        choices=['create', 'commit', 'pull', 'push', 'merge', 'release', 'rebase'],
                        help='The command to execute (e.g., create, commit, pull, push, merge, release, rebase).')
    parser.add_argument('-p', '--path', type=str, default='modules/', help='The parent path of the modules.')
    parser.add_argument('--commit-msg', type=str, default='Auto commit', help='Commit message for commit command.')
    parser.add_argument('--podfile-module', type=str, default='PodfileModule.yaml', help='Path to PodfileModule.yaml.')
    parser.add_argument('--podfile-local', type=str, default='PodfileLocal.yaml', help='Path to PodfileLocal.yaml.')

    args = parser.parse_args()

    # 获取当前工作目录
    current_path = os.getcwd()

    # 获取模块列表
    try:
        yaml_data = yaml_data(args.podfile_module)
        modules_list = load_data(yaml_data)
    except FileNotFoundError:
        debugInfo(f"Error: PodfileModule.yaml not found at {args.podfile_module}")
        return

    # 根据命令执行不同的操作
    if args.command == 'create':
        if not args.branch:
            debugInfo("Error: 'create' command requires a branch name with -b or --branch.")
            return
        result = create_branch(modules_list, args.path, args.branch, args.modules, current_path)
    elif args.command == 'commit':
        result = commit_branch(modules_list, args.modules, args.path, args.commit_msg)
    elif args.command == 'pull':
        result = pull_branch(modules_list, args.modules, args.path)
    elif args.command == 'push':
        result = push_branch(modules_list, args.modules, args.path)
    elif args.command == 'merge':
        if not args.branch:
            debugInfo("Error: 'merge' command requires a branch name to merge from with -b or --branch.")
            return
        result = merge_branch(args.modules, modules_list, args.path, args.branch)
    elif args.command == 'rebase':
        if not args.branch:
            debugInfo("Error: 'rebase' command requires a branch name to rebase from with -b or --branch.")
            return
        result = rebase_branch(args.modules, modules_list, args.path, args.branch)
    elif args.command == 'release':
        if not args.branch:
            debugInfo("Error: 'release' command requires a branch name to release from with -b or --branch.")
            return
        result = release_branch(modules_list, args.modules, args.path, current_path, args.branch)
    else:
        debugInfo("Error: Invalid command. Please use one of: create, commit, pull, push, merge, rebase, release.")
        return

    # 打印结果
    table = PrettyTable()
    table.field_names = ["Module", "Result", "Branch", "Message"]
    for status in result:
        status_str = "SUCCESS" if status.result == 1 else "FAILURE"
        table.add_row([status.module, status_str, status.branch, status.msg])
    print("\n--- Operation Results ---")
    print(table)


# 在脚本的最后调用 main 函数
if __name__ == '__main__':
    main()