
import { DatePicker, Form, Input, InputNumber, Modal, Select } from "antd";
import { useAppDispatch, useAppSelector } from "@/redux/hooks.ts";
import { useEffect, useMemo, useState } from "react";
import { OfferStatus, OfferType, UserDepartment } from "@/configs/constants.tsx";
import { createOffer, getOffers, updateOffer, deleteOffer } from "@/redux/features/offerSlice.ts";
import { useAuth } from "@/redux/hooks.ts";
import moment from "moment";
import { OfferPositionByDepartment } from '@/configs/constants.tsx'
import { useForm } from "antd/es/form/Form";
import { createCandidate, getCandidates, updateCandidate } from "@/redux/features/candidateSlice.ts";



export const ModalAddOffer = (props: any) => {
  const { role } = useAuth();
  const { initialValues, handleClose, isOpen } = props;
  const candidates = useAppSelector((state) => state.candidate.candidates);
  const users = useAppSelector((state) => state.user.users);

  const isDisable = ["Approved offer", "Rejected offer"].includes(initialValues?.status) && role !== "Admin"

  const userOptions = useMemo(
    () => users.map((user) => ({ label: user.username, value: user.id })),
    [users]
  );
  const candidateOptions = candidates.map((candidate) => ({ label: candidate.full_name, value: candidate.id }))
  const statusOptions = Object.values(OfferStatus).map((status) => ({ label: status, value: status }));
  const [department, setDepartment] = useState(null)
  const [positionOptionsByDept, setPositionOptionsByDept] = useState<any[]>([]);
  const [filteredCandidates, setFilteredCandidates] = useState([]);

  useEffect(() => {

    if (department) {
      setPositionOptionsByDept(OfferPositionByDepartment[department]);
      const filtered = candidates.filter(candidate =>
        candidate.department === department &&
        candidate.status === "Passed interview"  // Thêm điều kiện này
      );

      // Chuyển đổi sang format options cho Select
      const options = filtered.map(candidate => ({
        label: candidate.full_name,
        value: candidate.id
      }));
      setFilteredCandidates(options);
    } else {
      setPositionOptionsByDept([]);
      setFilteredCandidates([]);
    }
  }, [department, candidates]);
  const { user } = useAuth();
  const departmentOptions = useMemo(() => {
    if (user?.role === "Manager") {
      return [{ label: user.department, value: user.department }];
    }
    return Object.entries(UserDepartment).map(([_, value]) => ({
      label: value,
      value: value,
    }));
  }, [user]);

  const [form] = useForm();
  const formValues = Form.useWatch([], form);

  const dispatch = useAppDispatch();


  const handleChooseDepartment = (value) => {
    setDepartment(value);
    form.validateFields(["candidate_id"]);
  };

  const offerTypeOptions = Object.entries(OfferType).map(([_, value]) => ({ label: value, value: value }));

  const approverOptions = useMemo(() => {
    const hrUsers = users.filter((u) => u.role === "HR");
    return [
      { label: user.username, value: user.id },
      ...hrUsers.map((hrUser) => ({ label: hrUser.username, value: hrUser.id })),
    ];
  }, [users, user]);
  useEffect(() => {
    if (initialValues) {
      setDepartment(initialValues.department);

      // Format data cho form
      const formattedValues = {
        ...initialValues,
        contract_from: moment(initialValues.contract_from),
        contract_to: moment(initialValues.contract_to),
        candidate: {
          label: initialValues.candidate?.full_name,
          value: initialValues.candidate?.id
        },
        manager_id: {
          label: initialValues.manager?.username,
          value: initialValues.manager?.id
        },
        department: initialValues.department,
        contract_type: initialValues.contract_type,
        status: initialValues.status,
        basic_salary: initialValues.basic_salary,
        currency: initialValues.currency,
        note: initialValues.note
      };

      form.setFieldsValue(formattedValues);
    }
  }, [initialValues, form]);


  return (
    <Modal
      title={initialValues ? "EDIT OFFER" : "ADD OFFER"}
      open={isOpen}
      onCancel={handleClose}
      footer={null}
      className="text-xl"
      width={1000}
    >
      <Form
        form={form} // Kết nối với form đã khởi tạo
        name="layout-multiple-horizontal"
        layout="horizontal"
        className="w-full mt-10"
        onFinish={async (data) => {
          const { candidate, ...rest } = data;
          const payload = {
            ...rest,
            candidate_id: data.candidate?.value || data.candidate,
            manager_id: data.manager_id?.value || data.manager_id,
            interview_schedule_id: 1,
            position: data.position || "Backend Developer",
            level: data.level || "Junior 2.1",
            status: data.status
          };
          try {
            // Update candidate status based on offer status
            console.log('data: ', data)
            if (data.candidate) {
              const candidateId = data.candidate.id
              let newCandidateStatus;

              switch (data.status) {
                case 'Approved offer':
                  newCandidateStatus = 'Approved offer';
                  break;
                case 'Rejected offer':
                  newCandidateStatus = 'Rejected offer';
                  break;
                // Thêm các case khác nếu cần
              }

              if (newCandidateStatus) {
                await dispatch(updateCandidate({
                  id: candidateId,
                  payload: { status: newCandidateStatus }
                }));
              }
            }

            // Update/Create offer
            if (initialValues) {
              await dispatch(updateOffer({ payload, id: initialValues.id }));
            } else {
              await dispatch(createOffer(payload));
            }

            await dispatch(getOffers({}));
            handleClose();
          } catch (error) {
            console.error('Error:', error);
          }
        }}
        disabled={isDisable}
        initialValues={initialValues || { currency: "USD" }}
        labelCol={{ span: 6 }}
      >
        <div className="w-full flex justify-between">
          <Form.Item
            name="department"
            label="Department:"
            className="w-1/2"
            rules={[{ required: true, message: "Please select a department" }]}
          >
            <Select
              data-testid="select-offer-department"
              options={departmentOptions} onChange={(val) => handleChooseDepartment(val)} />
          </Form.Item>
          <Form.Item
            name="candidate"
            label="Candidate:"
            className="w-1/2 mr-5"
            rules={[
              { required: true, message: 'Please choose a candidate' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!getFieldValue('department')) {
                    return Promise.reject(new Error('Please choose the department first'));
                  }
                  return Promise.resolve();
                },
              }),
            ]}
          >
            <Select
              data-testid="select-offer-candidate"
              data-value={(() => {
                console.log('filteredCandidates:', filteredCandidates);
                console.log('form values:', formValues);

                // Log ra cả label được tìm thấy
                const foundLabel = formValues?.candidate?.full_name || '';
                console.log('Found candidate label:', foundLabel);

                return foundLabel || '';
              })()}

              options={filteredCandidates}

              onClick={() => {
                if (!department) {
                  form.setFields([
                    {
                      name: 'candidate',
                      errors: ['Please choose the department first'],
                    },
                  ]);
                }
              }}
            />
          </Form.Item>
        </div>




        <div className="w-full flex justify-between">
          <Form.Item
            name="manager_id"
            label="Approved by:"
            className="w-1/2 mr-5"
            rules={[{ required: true, message: 'Please enter approver' }]}
          >
            <Select
              data-testid="select-offer-approver"
              options={approverOptions}
            />
          </Form.Item>
          <Form.Item
            name="status"
            label="Status:"
            className="w-1/2"
            initialValue="Waiting for approval"
            rules={[{ required: true, message: 'Please enter status' }]}
          >
            <Select
              data-testid="select-offer-status"
              options={statusOptions}
            />
          </Form.Item>
        </div>
        <div className="w-full flex justify-between">
          <Form.Item
            name="contract_type"
            label="Type:"
            className="w-1/2 mr-5"
            rules={[{ required: true, message: 'Please enter type' }]}
          >
            <Select
              data-testid="select-offer-contract"
              options={offerTypeOptions}
            />
          </Form.Item>
          <Form.Item
            name="basic_salary"
            label="Basic Salary:"
            className="w-1/2"
            rules={[{ required: true, message: 'Please enter salary' }]}
          >
            <InputNumber
              data-testid="input-offer-salary"
              addonAfter={
                <Form.Item name="currency" noStyle>
                  {<Select style={{ width: 60 }} options={[{
                    value: 'USD',
                    label: '$'
                  },
                  {
                    value: 'EUR',
                    label: '€'
                  },
                  {
                    value: 'GBP',
                    label: '£'
                  },
                  {
                    value: 'CNY',
                    label: '¥'
                  }]} />}
                </Form.Item>
              }
              step={100}
              className="w-full"
              placeholder={"Enter salary from"}
            />
          </Form.Item>

        </div>
        <div className="w-full flex justify-between">
          <Form.Item
            name="contract_from"
            label="Contract From:"
            className="w-1/2 mr-5"
            rules={[{ required: true, message: 'Please enter time' }]}
          >
            <DatePicker
              data-testid="select-offer-from"
              className="w-full"
              disabledDate={(current) => current && current < moment().startOf('day')}
            />
          </Form.Item>
          <Form.Item
            name="contract_to"
            label="Contract To:"
            className="w-1/2"
            rules={[{ required: true, message: 'Please enter time' }]}
          >
            <DatePicker
              data-testid="select-offer-to"
              className="w-full"
              disabledDate={(current) => current && current < moment().startOf('day')}
            />
          </Form.Item>

        </div>
        <div className="w-full flex justify-between">
          <Form.Item
            name="note"
            label="Note:"
            className="w-full"
          >
            <Input
              data-testid="input-offer-note"
              allowClear
              placeholder={"Enter note"}
            />
          </Form.Item>
        </div>

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
};