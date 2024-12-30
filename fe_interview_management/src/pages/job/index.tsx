import { Button, Input, Select, Tag } from "antd";
import Helmet from "@/components/Helmet.tsx";
import { PlusOutlined } from "@ant-design/icons";
import { JobStatus } from "@/configs/constants.tsx";
import GenericTable from "@/components/Table";
import { useAppDispatch, useAppSelector, useAuth } from "@/redux/hooks.ts";
import { useEffect, useState } from "react";
import { deleteJob, getJobs } from "@/redux/features/jobSlice.ts";
import { ModalAddJob } from "@/components/modal/ModalAddJob.tsx";
import moment from "moment";
import dayjs from "dayjs";

const columns = [
  {
    title: "CODE",
    dataIndex: "id",
    key: "id",
    render: (id: number) => "JOB" + id,
},
  {
    title: 'Job Title',
    dataIndex: 'title',
    key: 'title',
  },
  {
    title: 'Required Skills',
    dataIndex: 'skills',
    key: 'skills',
    render: (skills: string[]) => {
      return skills?.map((skill) => {
        return <Tag key={skill}>{skill}</Tag>;
      });
    }
  },
  {
    title: 'Start date',
    dataIndex: 'start_date',
    key: 'start_date',
    render(v: any) {
      return moment(v).format('DD/MM/YYYY')
    }
  },
  {
    title: 'End date',
    dataIndex: 'end_date',
    key: 'end_date',
    render(v: any) {
      return moment(v).format('DD/MM/YYYY')
    }
  },
  {
    title: 'Level',
    dataIndex: 'level',
    key: 'level',
    render: (level: string[]) => {
      return level?.map((item) => {
        return <Tag key={item}>{item}</Tag>;
      });
    }
  },
  {
    title: 'Status',
    dataIndex: 'status',
    key: 'status',
  }
];

const statusOptions = Object.entries(JobStatus).map(([key, value]) => ({ label: value, value: key }));

export const ManageJob = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [selectedJob, setSelectedJob] = useState<any>(null);
  const [selectedStatus, setSelectedStatus] = useState<any>(undefined);
  const dispatch = useAppDispatch();
  const { role } = useAuth();
  const jobs = useAppSelector((state) => state.job.jobs);
  useEffect(() => {
    dispatch(getJobs({}));
  }, [selectedStatus]);

  const handleClose = () => {
    setSelectedJob(null);
    setIsModalVisible(false);
  }

  const handleDelete = async (id: number) => {
    await dispatch(deleteJob({ ids: [id + ""] }));
    await dispatch(getJobs({}));
  }

  const jobsData = [...jobs].reverse()

  return (
    <div className="bg-white p-10 h-full rounded">
      <Helmet title="Manage Job" />
      <ModalAddJob
        isOpen={isModalVisible}
        handleClose={handleClose}
        initialValues={selectedJob}
        key={selectedJob}
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
            onSearch={(search) => {
              dispatch(getJobs({ filter: JSON.stringify({ status: selectedStatus }), search }));
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
          Add Job
        </Button>
      </div>
      <div className="mt-5">
        <GenericTable
          columns={columns}
          data={jobsData}
          onDeleteItem={async (data) => { await handleDelete(data.id) }}
          onEditItem={(data) => {
            console.log(data);
            // @ts-ignore
            setSelectedJob({ ...data, end_date: dayjs(data.end_date), start_date: dayjs(data.start_date), skills: data.skills.map((skill: string) => ({ label: skill, value: skill })) });
            setIsModalVisible(true);
          }}
          showAction={role !== "Interviewer"}
        />
      </div>
    </div>
  );
}
