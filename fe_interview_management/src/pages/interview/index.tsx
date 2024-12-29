import { useEffect, useState } from "react";
import Helmet from "@/components/Helmet.tsx";
import { PlusOutlined } from "@ant-design/icons";
import GenericTable from "@/components/Table";
import { InterviewStatus } from "@/configs/constants.tsx";
import { ModalAddInterview } from "@/components/modal/ModalAddInterview.tsx";
import { useAppDispatch, useAppSelector, useAuth } from "@/redux/hooks.ts";
import { getJobs } from "@/redux/features/jobSlice.ts";
import { getCandidates } from "@/redux/features/candidateSlice.ts";
import { getUsers } from "@/redux/features/userSlice.ts";
import { getInterviews } from "@/redux/features/interviewSlice.ts";
import moment from "moment";
import dayjs from "dayjs";
import { Button, Input, Select, message } from "antd";
import axios from "axios";
const statusOptions = Object.entries(InterviewStatus).map(([key, value]) => ({ label: value, value: key }));
const columns = [
  {
    title: 'Interview title',
    dataIndex: 'title',
    key: 'interview_title',
  },
  {
    title: 'Candidate name',
    dataIndex: 'candidate',
    key: 'candidate',
    render: (_, data) => {
      return data?.candidate?.full_name;
    }
  },
  {
    title: 'Job title',
    dataIndex: 'job',
    key: 'job',
    render: (_, data) => {
      return data?.job?.title;
    }
  },
  {
    title: 'Schedule',
    dataIndex: 'schedule',
    key: 'schedule',
    render: (schedule, data) => {
      const date = moment(data.schedule_date).format("DD-MM-YYYY");
      const startTime = moment(data.schedule_time_from).format("HH:mm");
      const endTime = moment(data.schedule_time_to).format("HH:mm");
      return <div>
        <p>{date}</p>
        <p>{startTime} - {endTime}</p>
      </div>;
    }
  },
  {
    title: 'Status',
    dataIndex: 'status',
    key: 'status',
  }
];
export const InterviewPage = () => {
  const [selectedStatus, setSelectedStatus] = useState<any>();
  const [selectedInterview, setSelectedInterview] = useState<any>(undefined);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const { role } = useAuth();
  const dispatch = useAppDispatch();
  const interviews = useAppSelector((state) => {
    console.log('Current interviews state:', state.interview);
    return state.interview.interviews;
  });
  useEffect(() => {
    console.log('Interviews data changed:', interviews);
  }, [interviews]);

  useEffect(() => {
    dispatch(getJobs(undefined));
    dispatch(getCandidates(undefined));
    dispatch(getUsers(undefined));

  }, []);

  useEffect(() => {
    dispatch(getInterviews(undefined));
  }, [selectedStatus])

  useEffect(() => {
    // Call API when status changes with filter
    console.log('Selected status changed:', selectedStatus);
    if (selectedStatus) {
      console.log('Dispatching getInterviews with filter:', { status: selectedStatus });
      dispatch(getInterviews({ filter: JSON.stringify({ status: selectedStatus }) }));
    } else {
      console.log('Dispatching getInterviews without filter');
      dispatch(getInterviews(undefined));
    }
  }, [selectedStatus]);

  const handleClose = () => {
    setSelectedInterview(undefined);
    setIsModalVisible(false);
  }
  const handleDelete = async (record) => {
    try {

      const response = await axios.delete(`http://103.56.158.135:8086/api/v1/interview-schedule/${record.id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });


      if (response.status === 200) {
        message.success('Deleted successfully');
        // Refresh lại danh sách
        dispatch(getInterviews(undefined));
      }
    } catch (error) {
      message.error(error.response?.data?.message || 'Failed to delete interview');
    }
  };
  return (
    <div className="p-10 bg-white h-full rounded">
      <Helmet title="Manage Offer" />
      <ModalAddInterview
        isOpen={isModalVisible}
        handleClose={handleClose}
        initialValues={selectedInterview}
        key={selectedInterview}
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
          {/* <Input.Search
            className="w-1/6"
            onSearch={(search) => {
              dispatch(getInterviews({ filter: JSON.stringify({ status: selectedStatus }), search }));
            }}
            size="large"
          /> */}
        </div>
        <Button
          className="bg-blue-500 text-white p-5 rounded-lg"
          icon={<PlusOutlined />}
          onClick={() => setIsModalVisible(true)}
          disabled={role === "Interviewer"}
        >
          Add Interview
        </Button>
      </div>
      <div className="mt-5">
        <GenericTable
          columns={columns}
          data={interviews}
          onEditItem={(item) => {
            setSelectedInterview({
              ...item,
              schedule_date: dayjs(item.schedule_date),
              schedule_time_from: dayjs(item.schedule_time_from),
              schedule_time_to: dayjs(item.schedule_time_to),
              interviewer_ids: item.interviewers.map((interviewer) => ({ label: interviewer.full_name, value: interviewer.id })),
              candidate_id: { label: item.candidate.full_name, value: item.candidate.id },
              job_id: { label: item.job.title, value: item.job.id },
            });
            setIsModalVisible(true);
          }}
          onDeleteItem={handleDelete}
          showAction={role !== "Interviewer"}
        />
      </div>
    </div>
  );
}
