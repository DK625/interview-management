// @ts-nocheck
import { DatePicker, Form, Input, Modal, Select } from "antd";
import { useAppDispatch } from "@/redux/hooks.ts";
import { createUser, getUsers, updateUser } from "@/redux/features/userSlice.ts";
import { Gender, UserDepartment, UserRole, UserStatus } from "@/configs/constants.tsx";
import TextArea from "antd/es/input/TextArea";
import moment from "moment/moment";
import { useState, useEffect } from "react";
const genderOptions = Object.entries(Gender).map(([key, value]) => ({ label: value, value: value }));
const departmentOptions = Object.entries(UserDepartment).map(([key, value]) => ({
  label: value,
  value: value,
  'data-testid': `department-option-${value}` // Add test ID for each option
}));

const statusOptions = Object.entries(UserStatus).map(([key, value]) => ({
  label: value,
  value: value,
  'data-testid': `status-option-${value}`  // Add test ID for each status option
}));

const roleOptions = Object.entries(UserRole).map(([key, value]) => ({
  label: value,
  value: value,
  'data-testid': `role-option-${value}`  // Add test ID for each role option 
}));

export const ModalAddUser = (props: any) => {
  const { initialValues, handleClose, isOpen } = props;
  const dispatch = useAppDispatch();
  const [form] = Form.useForm();
  useEffect(() => {
    if (initialValues) {
      form.setFieldsValue(initialValues);
    } else {
      form.setFieldsValue({
        status: UserStatus.Active
      });
    }
  }, [initialValues, form]);


  return (
    <Modal
      title={initialValues ? "EDIT USER" : "ADD USER"}
      open={isOpen}
      onOk={() => { }}
      onCancel={handleClose}
      footer={[]}
      className="text-xl"
      width={900}
      afterClose={() => form.resetFields()}
    >
      <Form
        form={form}
        name="layout-multiple-horizontal"
        layout="horizontal"
        className="w-full mt-10"
        onFinish={async (data) => {
          console.log('data: ', data)
          const formatDob = (dobValue: any) => {
            if (!dobValue) return null;
            // Nếu là Moment object
            if (dobValue._isAMomentObject) {
              return dobValue.format("YYYY-MM-DD");
            }
            // Nếu là Date string
            return moment(dobValue).format("YYYY-MM-DD");
          };

          if (initialValues) {
            const payload = {
              ...data,
              dob: formatDob(data.dob)
            };

            await dispatch(updateUser({ payload, id: initialValues.id }));
            handleClose();
            dispatch(getUsers());
          } else {
            const payload = {
              ...data,
              dob: formatDob(data.dob),
              phone: data.phone || '0814117539', // giá trị mặc định cho phone
              gender: data.gender || 'Male', // giá trị mặc định cho gender
            };


            await dispatch(createUser(payload));
            form.resetFields();
            handleClose();
          }
        }}
        // initialValues={defaultValues}
        labelCol={{ span: 6 }}
        key={initialValues}
      >
        <div className="w-full flex justify-between">
          <Form.Item
            name="full_name"
            label="Full name:"
            className="w-1/2 mr-5"
            rules={[{ required: true, message: 'Please enter full name' }]}
          >
            <Input
              allowClear
              placeholder={"Enter full name"}
            />

          </Form.Item>

        </div>
        <div className="w-full flex justify-between">
          <Form.Item
            name="email"
            label="Email:"
            className="w-1/2"
            rules={[{ required: true, message: 'Please enter email' }]}
          >
            <Input
              allowClear
              placeholder={"Enter email"}
            />
          </Form.Item>
        </div>
        <div className="w-full flex justify-between">
          <Form.Item
            name="username"
            label="Username"
            className="w-1/2"
            // required
            rules={[{ required: true, message: 'Please enter username' }]}


          >
            <Input placeholder="Enter username"/>
          </Form.Item>
        </div>
        <div className="w-full flex justify-between">
          <Form.Item
            name="department"
            label="Department"
            className="w-1/2"
            rules={[{ required: true, message: 'Please select department' }]}
          >
            <Select
              options={departmentOptions}
              data-testid="department-select"  // Add this
              className="department-select"
            />
          </Form.Item>
        </div>

        <div className="w-full flex justify-between">
          <Form.Item
            name="role"
            label="Role:"
            className="w-1/2"
            rules={[{ required: true, message: 'Please enter role' }]}
          >
            <Select
              options={roleOptions}
              data-testid="role-select"    // Add test ID for select
              className="role-select"      // Add specific class
            />
          </Form.Item>
        </div>

        <div className="w-full flex justify-between">
          <Form.Item
            name="status"
            label="Status"
            className="w-1/2 mr-5"
            rules={[{ required: true, message: 'Please select status' }]}
          >
            <Select
              options={statusOptions}
              data-testid="status-select"    // Add test ID for select
              className="status-select"      // Add specific class
            />
          </Form.Item>
        </div>
        <Form.Item
          name="note"
          label="Note"
          className="w-full"
          labelCol={{ span: 3 }}
        >
          <TextArea
            allowClear
            placeholder={"Enter note"}
          />
        </Form.Item>
        <div className="w-full flex justify-end gap-x-5 mt-5">
          <Form.Item>
            <button
              className="border-blue-500 border px-4 py-2 text-blue-500 rounded"
              onClick={handleClose}
              type="button"
            >
              Close
            </button>
          </Form.Item>
          <Form.Item>
            <button
              className="bg-blue-500 hover:bg-blue-700 text-white py-2 px-5 rounded disabled:bg-gray-300 disabled:text-gray-500"
              type="submit"
            >
              Submit
            </button>
          </Form.Item>
        </div>
      </Form>
    </Modal>
  );
}
