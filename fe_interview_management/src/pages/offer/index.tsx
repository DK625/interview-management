// @ts-nocheck
import Helmet from "@/components/Helmet.tsx";
import { Button, Input, Select } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { JobStatus, OfferStatus, UserDepartment } from "@/configs/constants.tsx";
import { useEffect, useState } from "react";
import GenericTable from "@/components/Table";
import { ModalAddOffer } from "@/components/modal/ModalAddOffer.tsx";
import { useAppDispatch, useAppSelector } from "@/redux/hooks.ts";
import { getUsers } from "@/redux/features/userSlice.ts";
import { getCandidates } from "@/redux/features/candidateSlice.ts";
import { getInterviews } from "@/redux/features/interviewSlice.ts";
import moment from "moment";
import dayjs from "dayjs";
import { createOffer, getOffers, updateOffer, deleteOffer } from "@/redux/features/offerSlice.ts";
const statusOptions = Object.entries(OfferStatus).map(([key, value]) => ({ label: value, value: value }));
const departmentOptions = Object.entries(UserDepartment).map(([key, value]) => ({ label: value, value: value }));
const columns = [
  {
    title: 'Candidate Name',
    dataIndex: 'candidate',
    key: 'candidate_name',
    render: (_, data: any) => {
      return data?.candidate?.full_name;
    }
  },
  {
    title: 'Email',
    dataIndex: 'candidate',
    key: 'email',
    render: (_, data: any) => {
      return data?.candidate?.email;
    }
  },
  {
    title: 'Approver',
    dataIndex: 'manager',
    key: 'manager',
    render: (_, data: any) => {
      return data?.manager.full_name;
    }
  },
  {
    title: 'Department',
    dataIndex: 'department',
    key: 'department',
  },
  // {
  //   title: 'Position',
  //   dataIndex: 'position',
  //   key: 'position',
  // },
  {
    title: 'Status',
    dataIndex: 'status',
    key: 'status',
  }
];
export const OfferPage = () => {
  const [selectedStatus, setSelectedStatus] = useState<any>(undefined);
  const [selectedDepartment, setSelectedDepartment] = useState<any>(undefined);
  const [selectedOffer, setSelectedOffer] = useState<any>(undefined);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const dispatch = useAppDispatch();
  const offers = useAppSelector((state) => state.offer.offers);
  useEffect(() => {
    dispatch(getUsers({}));
    dispatch(getCandidates({}));
    dispatch(getInterviews({}));
    dispatch(getOffers({}));
  }, []);

  useEffect(() => {
    dispatch(getOffers({}));
  }, [selectedDepartment, selectedStatus]);

  const handleClose = () => {
    setSelectedDepartment(undefined);
    setSelectedStatus(undefined);
    setSelectedOffer(undefined);
    setIsModalVisible(false);
  }
  const handleDeleteOffer = async (record: any) => {
    await dispatch(deleteOffer(record.id));
    dispatch(getOffers({})); // Refresh lại danh sách sau khi xóa
  };

  return (
    <div className="p-10 bg-white h-full rounded">
      <Helmet title="Manage Offer" />
      <ModalAddOffer
        isOpen={isModalVisible}
        initialValues={selectedOffer}
        handleClose={handleClose}
        key={selectedOffer}
      />
      <div className="w-full flex justify-between items-center">
        <div className="flex w-9/12">
          <Select
            className="w-1/6 mr-2"
            placeholder="Select status"
            options={statusOptions}
            onChange={(value) => setSelectedStatus(value)}
            size="large"
            defaultValue={selectedStatus}
            allowClear
          />
          <Select
            className="w-1/6 mr-2"
            placeholder="Department"
            options={departmentOptions}
            size="large"
            onChange={(value) => setSelectedDepartment(value)}
            defaultValue={selectedDepartment}
            allowClear={true}
          />

          <Input.Search
            className="w-1/3"
            onSearch={(search) => {
              dispatch(getOffers({ filter: JSON.stringify({ status: selectedStatus, department: selectedDepartment }), search }));
            }}
            size="large"
          />
        </div>
        <Button
          className="bg-blue-500 text-white p-5 rounded-lg"
          icon={<PlusOutlined />}
          onClick={() => setIsModalVisible(true)}
        >
          Add Offer
        </Button>
      </div>
      <div className="mt-5">
        <GenericTable
          columns={columns}
          data={offers}
          onEditItem={(record) => {
            setSelectedOffer({
              ...record,
              contract_from: dayjs(record.contract_from),
              contract_to: dayjs(record.contract_to),
              candidate_id: { label: record.candidate.full_name, value: record.candidate.id },
              manager_id: { label: record.manager.full_name, value: record.manager.id },
              // interview_schedule_id: { label: record.interview_schedule.title, value: record.interview_schedule.id }
            });
            setIsModalVisible(true);
          }}
          onDeleteItem={handleDeleteOffer}
        />
      </div>
    </div>
  );
}
