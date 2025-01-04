import Helmet from "@/components/Helmet.tsx";
import { Button, Input, Select } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import GenericTable from "@/components/Table";
import { useEffect, useState } from "react";
import { CandidateStatus } from "@/configs/constants.tsx";
import { ModalAddCandidate } from "@/components/modal/ModalAddCandidate.tsx";
import { useAppDispatch, useAppSelector, useAuth } from "@/redux/hooks.ts";
import { deleteCandidate, getCandidates } from "@/redux/features/candidateSlice.ts";
import moment from "moment";
import dayjs from "dayjs";

const columns = [
  {
    title: 'Name',
    dataIndex: 'full_name',
    key: 'candidate_name',
  },
  {
    title: 'Email',
    dataIndex: 'email',
    key: 'email',
  },
  {
    title: 'Phone no',
    dataIndex: 'phone',
    key: 'phone',
  },
  {
    title: 'Position',
    dataIndex: 'position',
    key: 'position',
  },
  {
    title: 'Status',
    dataIndex: 'status',
    key: 'status',
    render: (status: string, record: any) => (
      <span data-testid={`candidate-status-${record.full_name}`}>{status}</span>
    )
  }
];
export const CandidatePage = () => {
  const [selectedStatus, setSelectedStatus] = useState<any>(undefined);
  const [selectedCandidate, setSelectedCandidate] = useState<any>(undefined);
  const dispatch = useAppDispatch();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const candidates = useAppSelector((state) => state.candidate.candidates);
  const statusOptions = Object.entries(CandidateStatus).map(([key, value]) => ({ label: value, value: value }));
  const { role } = useAuth();
  useEffect(() => {
    dispatch(getCandidates({}));
  }, [selectedStatus]);
  const handleClose = () => {
    setSelectedCandidate(undefined);
    setIsModalVisible(false);
  }
  const candidatesData = [...candidates].reverse()

  return (
    <div className="p-10 bg-white h-full rounded">
      <Helmet title="Manage Offer" />
      <ModalAddCandidate
        isOpen={isModalVisible}
        handleClose={handleClose}
        initialValues={selectedCandidate}
        key={selectedCandidate}
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
          <Input.Search
            className="w-1/3"
            onSearch={async (search) => {
              dispatch(getCandidates({ filter: JSON.stringify({ status: selectedStatus }), search }));
            }}
            size="large"
          />
        </div>
        <Button
          className="bg-blue-500 text-white p-5 rounded-lg"
          icon={<PlusOutlined />}
          disabled={role === "Interviewer"}
          onClick={() => setIsModalVisible(true)}
        >
          Add Candidate
        </Button>
      </div>
      <div className="mt-5">
        <GenericTable
          columns={columns}
          data={candidatesData}
          onDeleteItem={async (record) => {
            await dispatch(deleteCandidate(record.id));
            await dispatch(getCandidates({}));
          }}
          onEditItem={(record) => {
            setSelectedCandidate({ ...record, dob: dayjs(record.dob), skills: record.skills.map((skill: string) => ({ label: skill, value: skill })) });
            setIsModalVisible(true);
          }}
          showAction={role !== "Interviewer"}
        />
      </div>
    </div>
  )
}
