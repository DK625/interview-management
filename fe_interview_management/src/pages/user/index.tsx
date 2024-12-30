import Helmet from "@/components/Helmet.tsx";
import { Button, Input, Select } from "antd";
import { IUser, ROLE } from "@/interfaces";
import GenericTable from "@/components/Table";
import { UsergroupAddOutlined } from "@ant-design/icons";
import { useAppDispatch, useAppSelector } from "@/redux/hooks.ts";
import { useEffect, useState } from "react";
import { getUsers } from "@/redux/features/userSlice.ts";
import { ModalAddUser } from "@/components/modal/ModalAddUser.tsx";
import moment from 'moment'
import { deleteUser } from "@/redux/features/userSlice.ts";

const roleOptions = ROLE.map((role) => {
  return { label: role, value: role };
});

const columns = [
  {
    title: 'Name',
    dataIndex: 'full_name',
    key: 'username',
  },
  {
    title: 'Username',
    dataIndex: 'username',
    key: 'username',
  },
  {
    title: 'Email',
    dataIndex: 'email',
    key: 'email',
  },
  {
    title: 'Department',  // Đổi title từ 'Phone No' thành 'Department'
    dataIndex: 'department',  // Đổi dataIndex từ 'phone' thành 'department'
    key: 'department',    // Đổi key từ 'phone' thành 'department'
  },
  {
    title: 'Role',
    dataIndex: 'role',
    key: 'role',
  },
  {
    title: 'Status',
    dataIndex: 'status',
    key: 'status',
  }
];

export const ManageUser = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [user, setUser] = useState<IUser>();
  const [selectedRole, setSelectedRole] = useState<string | undefined>(undefined);
  const dispatch = useAppDispatch();
  const users = useAppSelector((state) => state.user.users);
  useEffect(() => {
    dispatch(getUsers({}));
  }, [selectedRole]);

  const handleClose = () => {
    setUser(undefined);
    setIsModalVisible(false);
  }
  const handleEdit = (record) => {
    // Log để debug

    const editUser = {
      id: record.id,
      username: record.username,
      email: record.email,
      phone: record.phone,
      department: record.department,
      role: record.role,
      status: record.status,
      gender: record.gender,
      dob: record.dob ? moment(record.dob) : null,
      note: record.note || '',
      address: record.address || '',
      full_name: record.full_name,
      password: record.password // nếu cần
    };


    setUser(editUser);
    setIsModalVisible(true);
  };

  const handleDelete = async (record) => {
    try {
      await dispatch(deleteUser(record.id));
      await dispatch(getUsers({}));
    } catch (error) {
      console.log('error: ', error)
    }
  };

  const usersData = [...users].reverse()



  return (
    console.log('users: ', users),
    <div className="p-10 bg-white h-full">
      <Helmet title="Manage User" />
      <ModalAddUser
        isOpen={isModalVisible}
        handleClose={handleClose}
        initialValues={user}
        key={user}
      />
      <div className="w-full flex justify-between items-center">
        <div className="flex w-9/12">
          <Select
            className="w-1/6 mr-2"
            placeholder="Select role"
            options={roleOptions}
            size="large"
            onChange={(value) => setSelectedRole(value)}
            defaultValue={selectedRole}
            allowClear
          />
          <Input.Search
            className="w-1/3"
            onSearch={(search) => {
              dispatch(getUsers({ filter: JSON.stringify({ role: selectedRole }), search: search }));
            }}
            size="large"
          />
        </div>
        <Button
          className="bg-blue-500 text-white p-5 rounded-lg"
          icon={<UsergroupAddOutlined />}
          onClick={() => setIsModalVisible(true)}
        >
          Add User
        </Button>
      </div>
      <div className="mt-5">
        <GenericTable
          columns={columns}
          data={usersData}
          enableAction={true}
          onEditItem={handleEdit}
          onDeleteItem={handleDelete}
          pagination={{ pageSize: 5, pageSizeOptions: ['5', '10', '15', '20'] }}
        />
      </div>
    </div>
  );
}
