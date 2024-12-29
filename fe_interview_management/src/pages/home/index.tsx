// @ts-nocheck
import Loading from "@/components/Loading";
import { useAppSelector } from "@/redux/hooks.ts";
import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, Rectangle, Tooltip, XAxis, YAxis } from "recharts";
import { DatePicker, message } from "antd";

import GenericTable from "@/components/Table";
import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import statiticApi from "@/api/statiticApi";
import { Query } from "@/vite-env";
import dayjs from "dayjs";
import customParseFormat from "dayjs/plugin/customParseFormat";
import advancedFormat from "dayjs/plugin/advancedFormat";
import localeData from "dayjs/plugin/localeData";
import weekday from "dayjs/plugin/weekday";
import weekOfYear from "dayjs/plugin/weekOfYear";
import weekYear from "dayjs/plugin/weekYear";
import { useAppDispatch } from "@/redux/hooks.ts";
import { getInterviews } from "@/redux/features/interviewSlice.ts";
dayjs.extend(customParseFormat);
dayjs.extend(advancedFormat);
dayjs.extend(weekday);
dayjs.extend(localeData);
dayjs.extend(weekOfYear);
dayjs.extend(weekYear);

// import moment from 'moment'
const CANDIDATE_COLUMNS = [
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
  }
];

const Home = () => {
  const dispatch = useAppDispatch();
  const interviews = useAppSelector((state) => state.interview.interviews);
  const currentUser = useAppSelector((state: any) => state.auth.currentUser);
  const [hasChecked, setHasChecked] = useState(false);

  useEffect(() => {
    if (currentUser) {
      dispatch(getInterviews(undefined));
    }
  }, [currentUser]);

  // Effect 2: Check và hiển thị alert khi có dữ liệu
  useEffect(() => {
    console.log('Current state:', {
      hasChecked,
      currentUser,
      interviews,
      isManager: currentUser?.role === 'Manager',
      hasResults: !!interviews
    });

    // Chỉ check và set hasChecked khi đã có interviews
    if (!hasChecked && currentUser?.role === 'Manager' && interviews?.length > 0) {
      console.log('Checking for pending interviews');

      const pendingInterviews = interviews.filter(interview => {
        const hasCurrentUser = interview.interviewers.some(
          interviewer => interviewer.username === currentUser.username
        );
        console.log('Interview:', {
          status: interview.status,
          hasCurrentUser,
          interviewers: interview.interviewers
        });

        return interview.status === 'Invited' && hasCurrentUser;
      });

      console.log('Found pending interviews:', pendingInterviews);

      if (pendingInterviews?.length > 0) {
        message.info(
          <div className="text-start">
            <p>
              You have {pendingInterviews.length} pending interview waiting for
              your response:
            </p>
            <ul className="list-disc pl-4">
              {pendingInterviews.map((item) => (
                <li key={item.id}>{`${item.candidate.full_name} in ${
                  item.location
                } at ${dayjs(item.schedule_date).format("DD-MM-YYYY")}`}</li>
              ))}
            </ul>
          </div>
        );
      }
      // Chỉ set hasChecked sau khi đã có data và check xong
      setHasChecked(true);
    }
  }, [interviews, currentUser, hasChecked]);



  if (!currentUser) {
    return <Loading />
  }

  const [date, setDate] = useState(dayjs())
  const [query, setQuery] = useState<Query>({ page: 1, limit: 10 })

  const { data } = useQuery({
    queryKey: ['candidate_distribution'], queryFn: () => {
      return statiticApi.candidateDistribution()
    }
  })



  const { data: dashboard } = useQuery({
    queryKey: ['dashboard'], queryFn: () => {
      return statiticApi.dashboard()
    }
  })

  const { data: candidateStatus } = useQuery({
    queryKey: ['candidate_status'], queryFn: () => {
      return statiticApi.candidateStatus(query)
    }
  })

  const { data: jobs } = useQuery({
    queryKey: ['job', date.get('year')], queryFn: () => {
      return statiticApi.jobStatitics(date.get('year'))
    }
    ,

  })


  //orange, green, blue, yellow, purple, pink, red, cyan, lime, teal, indigo, violet, fuchsia, emerald, amber, gray, slate, rose, warmGray, trueGray, coolGray, blueGray
  const COLORS = ['#FF8C00', '#008000', '#0000FF', '#800080', '#FF0000', '#00FFFF', '#00FF00', '#008080', '#4B0082', '#FF1493', '#FF00FF', '#008000', '#FF4500', '#808080', '#708090', '#FF007F', '#2F4F4F', '#FF69B4', '#00FF7F', '#4682B4', '#FF6347', '#00CED1', '#9400D3', '#FFD700', '#FFA07A', '#00FF00', '#00FA9A']

  return (
    <div className="rounded p-10">
      <div className="flex h-[30%] pb-10 justify-between gap-10">
        <div className="flex-1 h-full shadow-lg rounded-lg bg-white p-3 pt-5">
          <span className="uppercase">Total candidate</span>
          <div className="flex-1 flex justify-around">
            <h1 className="font-extralight text-center mt-10 text-4xl">{dashboard?.data?.[0] ?? 0}</h1>
            <img src="/assets/total_candidate.jpg" className="w-3/12 h-[80px] object-contain" />
          </div>
        </div>
        <div className="flex-1 h-full shadow-lg rounded-lg bg-white p-3 pt-5">
          <span className="uppercase">Total Jobs</span>
          <div className="flex-1 flex justify-around">
            <h1 className="font-extralight text-center mt-10 text-4xl">{dashboard?.data?.[1] ?? 0}</h1>
            <img src="/assets/total_job.jpg" className="w-3/12 h-[80px] object-contain" />          </div>
        </div>
        <div className="flex-1 h-full shadow-lg rounded-lg bg-white p-3 pt-5 flex flex-col">
          <span className="uppercase">Job Applied</span>
          <div className="flex-1 flex justify-around">
            <h1 className="font-extralight text-center mt-10 text-4xl">{dashboard?.data?.[2] ?? 0}</h1>
            <img src="/assets/job_applied.jpg" className="w-3/12 h-[80px] object-contain" />
          </div>
        </div>
        <div className="flex-1 h-full shadow-lg rounded-lg bg-white p-3 pt-5 flex flex-col">
          <span className="uppercase">Oncoming schedule</span>
          <div className="flex-1 flex justify-around">
            <h1 className="font-extralight text-center mt-10 text-4xl">{dashboard?.data?.[3] ?? 0}</h1>
            <img src="/assets/oncoming_schedule.jpg" className="w-3/12 h-[80px] object-contain" />
          </div>
        </div>
      </div>
      <div className="rounded bg-white mt-2 h-[60vh] shadow-md p-5">
        <div className="flex justify-between">
          <h3 className="font-semibold text-xl">Job Statistic</h3>
          <DatePicker
            picker="year"
            defaultValue={date}
            onChange={(value) => {
              setDate(value)
            }}
          />
        </div>
        <div className="flex gap-10 justify-between items-center mt-10">
          <BarChart
            width={1300}
            height={400}

            data={jobs?.data ?? []}
            margin={{
              top: 5,
              right: 10,
              left: 10,
              bottom: 5,
            }}
          >
            {/*<CartesianGrid strokeDasharray="3 3" />*/}
            <XAxis domain={[1, 'auto']} dataKey="name" />
            <YAxis type="number" domain={[1, Math.max(5, ...jobs?.data?.map(it => it.val) || [])]} />
            <Tooltip />
            <Legend />
            <Bar dataKey="val" stackId="a" fill="#5B32EA" radius={5} activeBar={<Rectangle fill="pink" radius={5} />} name={'Job Apply'} />
            <Bar dataKey="value" stackId="a" fill="#17BE98" radius={5} activeBar={<Rectangle fill="red" radius={5} />} name={'Job Not Apply'} />
          </BarChart>
        </div>
      </div>
      <div className="mt-5 h-[40vh] flex justify-between gap-5">
        <div className="w-8/12 bg-white rounded shadow-md h-full p-5">
          <h3 className="font-semibold text-xl mb-5">Candidate Status</h3>
          <GenericTable columns={CANDIDATE_COLUMNS} data={candidateStatus?.data?.results ?? []} />
        </div>
        <div className="w-4/12 bg-white rounded shadow-md h-full p-5">
          <h3 className="font-semibold text-xl mb-5">Candidate Distribution</h3>
          <PieChart width={400} height={270}>
            <Pie
              data={data?.data ?? []}
              labelLine={false}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {data?.data.map((entry: any, index: number) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} name={entry?.status} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </div>
      </div>
    </div>
  )
}
export default Home;
