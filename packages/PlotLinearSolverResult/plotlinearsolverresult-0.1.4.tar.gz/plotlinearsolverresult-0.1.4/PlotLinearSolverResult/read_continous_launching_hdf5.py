# -*- encoding: utf-8 -*-
'''
Filename         :read_continous_launching_hdf5.py
Description      :
Time             :2023/04/15 11:01:37
Author           :Zhengquan Liu
Version          :1.0
'''

import h5py
import numpy as np

def print_to_dset(h5obj,depth=0):
    """
    Print all directoty information in the h5 object to the dataset
    Arguments
    ---------
    h5obj : h5py._hl.group.File or h5py._hl.group.Group
        a h5 object
    Returns
    -------
    none
    """
    if type(h5obj) == h5py._hl.dataset.Dataset:
        return h5obj.name
    dset_paths = []
    items = list(h5obj.keys())
    for index,item in enumerate(items):
        if str.isdigit(item):
            continue
        # 是否是最后一个元素
        is_last = index == len(items)-1
        # 得到下一级的h5对象
        item_h5obj = h5obj[item]
        print("   "*depth,end="")
        if is_last:
            print("└──",end="")
        else:
            print("├──",end="")

        print(item)
        dset_paths.append(print_to_dset(item_h5obj,depth+1))

    return dset_paths



class H5File_CL:
    def __init__(self,filepath) -> None:
        self.h5file = h5py.File(filepath,'r')

    def print_directory_information(self):
        return print_to_dset(self.h5file)
    
    def get_numTimes(self):
        """
        Get the number of time steps.
        """
        return len(self.h5file['TimeStamps'])
    
    def get_data_over_time(self,group):
        """
        Get the data over time.
        """
        data = []
        for i in range(self.get_numTimes()):
            data.append(group[str(i)])
        return np.array(data)

    def get_TimesStamps(self):
        """
        Get the time stamps.
        """
        timeStamps_group = self.h5file['TimeStamps']
        return self.get_data_over_time(timeStamps_group)
    
    def get_launching_time_points(self):
        """
        得到发射间隔时间点
        Get launch interval time points.
        e.g. 0--launch1--77,78--wait launch2--108,109--launch2--189
        return [0,78,109,189]
        """
        res = []
        keys = self.h5file['ProjBCoord'].keys() # 得到所有的key，即launching所有的时间点
        pre_step_is_in = False
        for i in range(self.get_numTimes()):
            this_step_is_in = str(i) in keys
            if  pre_step_is_in ^ this_step_is_in: # 异或
                res.append(i)
            pre_step_is_in = this_step_is_in
        res.append(self.get_numTimes())
        return res
    
    def get_num_periods(self):
        """
        得到launching和wait launch的总数
        """
        index_vec = self.get_launching_time_points()
        return len(index_vec)-1
    
    def get_num_launching(self):
        """
        得到launching的总数
        """
        return int((self.get_num_periods() + 1)/2)
    
    def get_time_point_range_in_specified_period(self,period_num):
        """
        得到指定时间段的时间点
        Get the time point for the specified time period.
        """
        if period_num == self.get_num_periods():
            return range(self.get_launching_time_points()[period_num-1],self.get_launching_time_points()[-1])
        else:
            return range(self.get_launching_time_points()[period_num-1], self.get_launching_time_points()[period_num]-1)
    
    def get_time_point_range_in_specified_state(self,state_num):
        """
        得到指定状态的时间段
        Get the time period for the specified state.
        e.g. 0--launch1--77,78--wait launch2--108,109--launch2--189
        这里认为第一个状态为launch1和wait launch2，第二个状态为launch2
        """
        if state_num*2 > self.get_num_periods():
            return range(self.get_launching_time_points()[state_num*2-2],self.get_launching_time_points()[-1])
        else:
            return range(self.get_launching_time_points()[state_num*2-2],self.get_launching_time_points()[state_num*2]-1)
        
    def get_time_point_range_in_specified_launching(self,launch_num):
        """
        得到指定发射的时间段
        Get the time period for the specified launching.
        """
        if launch_num == self.get_num_launching():
            return range(self.get_launching_time_points()[launch_num*2-2],self.get_launching_time_points()[-1])
        else:
            return range(self.get_launching_time_points()[launch_num*2-2], self.get_launching_time_points()[launch_num*2-1]-1)
    
    def get_time_point_range_in_after_specified_launching(self,launch_num):
        """
        得到指定发射后的时间段
        Get the time period after the specified launching.
        """
        return range(self.get_launching_time_points()[launch_num*2-1], self.get_launching_time_points()[launch_num*2]-1)
    
    def get_projB_coord(self,launch_num):
        """
        得到指定发射的时间段的弹箭广义坐标ProjBCoord
        Get the ProjBCoord for the specified launching.
        type: np.array
        shape: (time_step,6)
        """
        group_ProjBCoord = self.h5file['ProjBCoord']
        data = []
        for i in self.get_time_point_range_in_specified_launching(launch_num):
            data.append(group_ProjBCoord[str(i)])
        return np.array(data)

    def get_projB_vel(self,launch_num):
        """
        得到指定发射的时间段的弹箭广义速度ProjBVel
        Get the ProjBVel for the specified launching.
        type: np.array
        shape: (time_step,6)
        """
        group_ProjBVel = self.h5file['ProjBVel']
        data = []
        for i in self.get_time_point_range_in_specified_launching(launch_num):
            data.append(group_ProjBVel[str(i)])
        return np.array(data)
    
    def get_projB_acc(self,launch_num):
        """
        得到指定发射的时间段的弹箭广义加速度ProjBAcc
        Get the ProjBAcc for the specified launching.
        type: np.array
        shape: (time_step,6)
        """
        group_ProjBAcc = self.h5file['ProjBAcc']
        data = []
        for i in self.get_time_point_range_in_specified_launching(launch_num):
            data.append(group_ProjBAcc[str(i)])
        return np.array(data)
    
    def get_modal_coord(self):
        """
        得到所有时间的模态坐标
        Get modal coordinates for all time.
        """
        group_ModalCoord = self.h5file['ModalCoord']
        return self.get_data_over_time(group_ModalCoord)
    
    def get_modal_vel(self):
        """
        得到所有时间的模态速度
        Get modal velocity for all time.
        """
        group_ModalVel = self.h5file['ModalVel']
        return self.get_data_over_time(group_ModalVel)
    
    def get_modal_acc(self):
        """
        得到所有时间的模态加速度
        Get modal acceleration for all time.
        """
        group_ModalAcc = self.h5file['ModalAcc']
        return self.get_data_over_time(group_ModalAcc)
    
    def get_bodys_infor(self):
        """
        得到所有的元件信息
        Get all the information of the elements.
        """
        group_state0_bodys = self.h5file['/ModalInformations/State_0/Bodys']
        for body in group_state0_bodys.keys():
            print(body+': ',end="")
            group_Body_i = group_state0_bodys[body]
            if len(group_Body_i.keys()) > 5:
                print('beam, ',end="")
                print('number of nodes: ' + str(len(group_Body_i.keys())))
            else:
                print('rb')

    def get_rb_Phi_I1(self,state_num,rb_id):
        """
        得到指定状态指定刚体的Phi_I1
        Get the Phi_I1 of the specified rigid body in the specified state.
        """
        str_State_i = 'State_' + str(state_num-1)
        str_Body_i = 'Body_' + str(rb_id)
        dateset_Phi_I1 = self.h5file['/ModalInformations/'+str_State_i+'/Bodys/'+str_Body_i+'/Phi_I1']
        return np.array(dateset_Phi_I1)

    def get_beam_Phi_i(self,state_num,beam_id,node_id):
        """
        得到指定状态指定梁指定节点编号的Phi_i
        Get the Phi_i of the specified beam and node in the specified state.
        """
        str_State_i = 'State_' + str(state_num-1)
        str_Body_i = 'Body_' + str(beam_id)
        dataset_Phi_i = self.h5file['/ModalInformations/'+str_State_i+'/Bodys/'+str_Body_i+'/'+str(node_id)]
        return np.array(dataset_Phi_i)
    
    def cal_rb_I1_phy_coord(self,rb_id):
        """
        计算指定刚体的物理坐标
        Cal the physical coordinates of the specified rigid body.
        """
        res = []
        modal_coord = self.get_modal_coord()
        num_launching = self.get_num_launching()
        for i in range(num_launching):
            Phi_I1 = self.get_rb_Phi_I1(i+1,rb_id)
            range_i = self.get_time_point_range_in_specified_state(i+1)
            res.append(np.matmul(modal_coord[range_i],Phi_I1))
        return np.concatenate(res)
    
    def cal_rb_I1_phy_vel(self,rb_id):
        """
        计算指定刚体的物理速度
        Cal the physical velocity of the specified rigid body.
        """
        res = []
        modal_vel = self.get_modal_vel()
        num_launching = self.get_num_launching()
        for i in range(num_launching):
            Phi_I1 = self.get_rb_Phi_I1(i+1,rb_id)
            range_i = self.get_time_point_range_in_specified_state(i+1)
            res.append(np.matmul(modal_vel[range_i],Phi_I1))
        return np.concatenate(res)
    
    def cal_rb_I1_phy_acc(self,rb_id):
        """
        计算指定刚体的物理加速度
        Cal the physical acceleration of the specified rigid body.
        """
        res = []
        modal_acc = self.get_modal_acc()
        num_launching = self.get_num_launching()
        for i in range(num_launching):
            Phi_I1 = self.get_rb_Phi_I1(i+1,rb_id)
            range_i = self.get_time_point_range_in_specified_state(i+1)
            res.append(np.matmul(modal_acc[range_i],Phi_I1))
        return np.concatenate(res)
    
    def cal_beam_node_i_phy_coord(self,beam_id,node_id):
        """
        计算指定梁指定节点的物理坐标
        Cal the physical coordinates of the specified beam and node.
        """
        res = []
        modal_coord = self.get_modal_coord()
        num_launching = self.get_num_launching()
        for i in range(num_launching):
            Phi_i = self.get_beam_Phi_i(i+1,beam_id,node_id)
            range_i = self.get_time_point_range_in_specified_state(i+1)
            res.append(np.matmul(modal_coord[range_i],Phi_i))
        return np.concatenate(res)

    def cal_beam_node_i_phy_vel(self,beam_id,node_id):
        """
        计算指定梁指定节点的物理速度
        Cal the physical velocity of the specified beam and node.
        """
        res = []
        modal_vel = self.get_modal_coord()
        num_launching = self.get_num_launching()
        for i in range(num_launching):
            Phi_i = self.get_beam_Phi_i(i+1,beam_id,node_id)
            range_i = self.get_time_point_range_in_specified_state(i+1)
            res.append(np.matmul(modal_vel[range_i],Phi_i))
        return np.concatenate(res)

    def cal_beam_node_i_phy_acc(self,beam_id,node_id):
        """
        计算指定梁指定节点的物理加速度
        Cal the physical acceleration of the specified beam and node.
        """
        res = []
        modal_acc = self.get_modal_coord()
        num_launching = self.get_num_launching()
        for i in range(num_launching):
            Phi_i = self.get_beam_Phi_i(i+1,beam_id,node_id)
            range_i = self.get_time_point_range_in_specified_state(i+1)
            res.append(np.matmul(modal_acc[range_i],Phi_i))
        return np.concatenate(res)



    # todo:得到有几个元件有几个状态有几个